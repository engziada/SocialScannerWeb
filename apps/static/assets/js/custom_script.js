
function openConfirmationModal(message, url) {
    document.getElementById('modal-message').innerHTML = message;
    document.getElementById('callback-url').value = url;
    //document.getElementById('modal-default').classList.add('show');
}

document.getElementById('confirm-delete-btn').addEventListener('click', function () {
    var callbackUrl = document.getElementById('callback-url').value;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', callbackUrl);
    xhr.onload = function () {
        if (xhr.status === 200) {
            window.location.reload();
        } else {
            alert('Error occurred during deletion. Please try again.');
        }
    };
    xhr.send();
});
