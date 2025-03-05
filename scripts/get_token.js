// Paste the following in the devtools at https://note.yctf.ch after logging in
console.log(localStorage.getItem("JWT"));

// Otherwise, you can use the following bookmarklet
javascript: (function () {
	const jwt = localStorage.getItem("JWT");
	if (jwt) {
		navigator.clipboard.writeText(jwt).then(() => alert("JWT copied to clipboard!"));
	} else {
		alert("JWT not found.");
	}
})();
