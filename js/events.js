document.addEventListener('DOMContentLoaded', () => {
    const ELEMENTS = {
        eventCheckboxes: document.querySelectorAll('.event-checkbox'),
        selectAllCheckbox: document.getElementById('select-all-events'),
        selectedCountSpan: document.getElementById('selected-count'),
        downloadBtn: document.getElementById('download-selected-ics'),
        googleCalendarButtons: document.querySelectorAll('.google-calendar'),
        showUpcomingBtn: document.getElementById('show-upcoming'),
        showPastBtn: document.getElementById('show-past'),
        showAllBtn: document.getElementById('show-all'),
        eventCards: document.querySelectorAll('.event-card')
    };

    const UTILS = {
        formatDate: (date) => {
            return `${date.toISOString().replace(/[-:]/g, '').split('.')[0]}Z`;
        },

        getSelectedCount: () => {
            return document.querySelectorAll('.event-checkbox:checked').length;
        },

        getSelectedEvents: () => {
            const checkedBoxes = document.querySelectorAll('.event-checkbox:checked');
            return Array.from(checkedBoxes).map(checkbox => ({
                title: checkbox.dataset.eventTitle,
                start: checkbox.dataset.eventStart,
                end: checkbox.dataset.eventEnd,
                location: checkbox.dataset.eventLocation,
                description: checkbox.dataset.eventDescription
            }));
        },

        isPastEvent: (dateString) => {
            try {
                const eventDate = new Date(dateString);
                const now = new Date();
                return eventDate < now;
            } catch {
                return false;
            }
        },

        updateEventStatuses: () => {
            ELEMENTS.eventCards.forEach(card => {
                const startDate = card.dataset.eventStart;
                const isPast = UTILS.isPastEvent(startDate);
                card.dataset.eventStatus = isPast ? 'past' : 'upcoming';

                if (isPast) {
                    card.classList.add('past-event');
                    card.classList.remove('upcoming-event');
                } else {
                    card.classList.add('upcoming-event');
                    card.classList.remove('past-event');
                }
            });
        },

        filterEvents: (filter) => {
            ELEMENTS.eventCards.forEach(card => {
                const status = card.dataset.eventStatus;
                const shouldShow = filter === 'all' || status === filter;
                card.style.display = shouldShow ? 'block' : 'none';
            });
        },

        setActiveButton: (activeBtn) => {
            [ELEMENTS.showUpcomingBtn, ELEMENTS.showPastBtn, ELEMENTS.showAllBtn].forEach(btn => {
                btn.classList.remove('active', 'bg-primary', 'text-primary-foreground');
                btn.classList.add('bg-secondary', 'text-secondary-foreground');
            });
            activeBtn.classList.add('active', 'bg-primary', 'text-primary-foreground');
            activeBtn.classList.remove('bg-secondary', 'text-secondary-foreground');
        }
    };

    const createICS = (events) => {
        const calendarStart = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Y-CTF//Events//EN'
        ];

        const calendarEnd = ['END:VCALENDAR'];

        const eventEntries = events.map((event, index) => {
            const start = new Date(event.start);
            const end = new Date(event.end);

            return [
                'BEGIN:VEVENT',
                `UID:${Date.now()}-${index}@yctf.ch`,
                `DTSTAMP:${UTILS.formatDate(new Date())}`,
                `DTSTART:${UTILS.formatDate(start)}`,
                `DTEND:${UTILS.formatDate(end)}`,
                `SUMMARY:${event.title}`,
                `DESCRIPTION:${event.description}`,
                `LOCATION:${event.location}`,
                'END:VEVENT'
            ].join('\r\n');
        });

        return [...calendarStart, ...eventEntries, ...calendarEnd].join('\r\n');
    };

    const downloadFile = (content, filename, filetype) => {
        const blob = new Blob([content], { type: filetype });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const updateCheckboxVisual = (checkbox) => {
        const label = checkbox.closest('label');
        const checkboxDiv = label.querySelector('div:first-of-type');
        const glowRing = label.querySelector('.absolute.inset-0');

        if (checkbox.checked) {
            checkboxDiv.classList.add('bg-primary', 'border-primary');
            checkboxDiv.classList.remove('border-border', 'bg-background/80');
            glowRing?.classList.add('scale-110');
            glowRing?.classList.remove('scale-0');
        } else {
            checkboxDiv.classList.remove('bg-primary', 'border-primary');
            checkboxDiv.classList.add('border-border', 'bg-background/80');
            glowRing?.classList.remove('scale-110');
            glowRing?.classList.add('scale-0');
        }
    };

    const updateSelectAllVisual = () => {
        const label = ELEMENTS.selectAllCheckbox.closest('label');
        const checkboxDiv = label.querySelector('div');

        if (ELEMENTS.selectAllCheckbox.indeterminate) {
            checkboxDiv.classList.add('bg-primary/50', 'border-primary');
            checkboxDiv.classList.remove('border-border', 'bg-primary', 'bg-background');
        } else if (ELEMENTS.selectAllCheckbox.checked) {
            checkboxDiv.classList.add('bg-primary', 'border-primary');
            checkboxDiv.classList.remove('border-border', 'bg-primary/50', 'bg-background');
        } else {
            checkboxDiv.classList.remove('bg-primary', 'border-primary', 'bg-primary/50');
            checkboxDiv.classList.add('border-border', 'bg-background');
        }
    };

    const updateSelectionState = () => {
        const selectedCount = UTILS.getSelectedCount();
        const totalCount = ELEMENTS.eventCheckboxes.length;

        ELEMENTS.selectedCountSpan.textContent = selectedCount;
        ELEMENTS.downloadBtn.disabled = selectedCount === 0;
        ELEMENTS.selectAllCheckbox.indeterminate = selectedCount > 0 && selectedCount < totalCount;
        ELEMENTS.selectAllCheckbox.checked = selectedCount === totalCount;

        updateSelectAllVisual();
    };

    const handleSelectAll = () => {
        const shouldCheck = ELEMENTS.selectAllCheckbox.checked;
        for (const checkbox of ELEMENTS.eventCheckboxes) {
            checkbox.checked = shouldCheck;
            updateCheckboxVisual(checkbox);
        }
        updateSelectionState();
    };

    const downloadSelectedEvents = () => {
        const selectedEvents = UTILS.getSelectedEvents();
        if (selectedEvents.length === 0) return;

        const icsContent = ICS.createICS(selectedEvents);
        const filename = `y-ctf-events-${new Date().toISOString().split('T')[0]}.ics`;
        FILE.downloadFile(icsContent, filename, 'text/calendar');
    };


    const GOOGLE_CALENDAR = {
        buildUrl: (event) => {
            const startDate = UTILS.formatDate(event.start);
            const endDate = UTILS.formatDate(event.end);

            return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(event.title)}&dates=${startDate}/${endDate}&details=${encodeURIComponent(event.description)}&location=${encodeURIComponent(event.location)}`;
        },

        openEvent: (button) => {
            const eventData = {
                title: button.dataset.eventTitle,
                start: new Date(button.dataset.eventStart),
                end: new Date(button.dataset.eventEnd),
                location: button.dataset.eventLocation,
                description: button.dataset.eventDescription
            };

            const url = GOOGLE_CALENDAR.buildUrl(eventData);
            window.open(url, '_blank');
        }
    };

    const bindEvents = () => {
        ELEMENTS.showUpcomingBtn?.addEventListener('click', () => {
            UTILS.setActiveButton(ELEMENTS.showUpcomingBtn);
            UTILS.filterEvents('upcoming');
        });

        ELEMENTS.showPastBtn?.addEventListener('click', () => {
            UTILS.setActiveButton(ELEMENTS.showPastBtn);
            UTILS.filterEvents('past');
        });

        ELEMENTS.showAllBtn?.addEventListener('click', () => {
            UTILS.setActiveButton(ELEMENTS.showAllBtn);
            UTILS.filterEvents('all');
        });

        for (const checkbox of ELEMENTS.eventCheckboxes) {
            checkbox.addEventListener('change', () => {
                updateCheckboxVisual(checkbox);
                updateSelectionState();
            });
        }

        ELEMENTS.selectAllCheckbox.addEventListener('change', handleSelectAll);

        ELEMENTS.downloadBtn.addEventListener('click', downloadSelectedEvents);

        for (const button of ELEMENTS.googleCalendarButtons) {
            button.addEventListener('click', (e) => {
                GOOGLE_CALENDAR.openEvent(e.target.closest('button'));
            });
        }
    };

    bindEvents();
    ELEMENTS.eventCheckboxes.forEach(updateCheckboxVisual);
    updateSelectAllVisual();
    updateSelectionState();

    UTILS.updateEventStatuses();
    UTILS.filterEvents('upcoming');
});