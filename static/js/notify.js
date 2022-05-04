console.log('notify.js loaded');
function close_popup() {
    console.log('closing popup');
    $('#myPopup').remove();
};
document.getElementById('myPopup').classList.toggle('show');
setTimeout(close_popup, 5800);