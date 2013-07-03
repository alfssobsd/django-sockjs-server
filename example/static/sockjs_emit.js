SockJS.prototype.emit = function (token, data) {
    var meta_dict = {
        token:token,
        data:data
    };
    this.send(JSON.stringify(meta_dict))
};