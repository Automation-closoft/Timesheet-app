document.addEventListener("DOMContentLoaded", () => {
    // Get today's date in the format YYYY-MM-DD
    const today = new Date().toISOString().split('T')[0];

    // Select the date input field
    const dateInput = document.getElementById("date");

    // Set the 'min' and 'max' attributes to restrict date selection to today
    dateInput.setAttribute('min', today);
    dateInput.setAttribute('max', today);

    // Select the form and attach the submit event listener for time validation
    const form = document.querySelector("form");
    
    form.addEventListener("submit", (event) => {
        // Get the login and logout times from the input fields
        const loginTime = document.getElementById("login-time").value;
        const logoutTime = document.getElementById("logout-time").value;

        // Check if the logout time is earlier than or equal to the login time
        if (logoutTime <= loginTime) {
            // Show an alert and prevent form submission if validation fails
            alert("Log Out time must be later than Log In time!");
            event.preventDefault();
        }
    });
});