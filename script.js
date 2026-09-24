console.log("KYC Monitor loaded successfully");


setTimeout(function () {

    const alerts =
        document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        alert.style.display = "none";

    });

}, 5000);