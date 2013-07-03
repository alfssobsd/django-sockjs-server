SockJS.prototype.emit = function (token, data) { // wrapper around SockJS.send for djazator's protocol support
    var meta_dict = {
        token:token,
        data:data
    };
    this.send(JSON.stringify(meta_dict))
};