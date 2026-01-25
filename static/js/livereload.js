// Live reload functionality for development
(function() {
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        // Only enable live reload on localhost
        return;
    }

    const socket = io();

    socket.on('reload', function() {
        console.log('File change detected, reloading page...');
        location.reload();
    });

    socket.on('connect', function() {
        console.log('Live reload connected');
    });

    socket.on('disconnect', function() {
        console.log('Live reload disconnected');
    });
})();
