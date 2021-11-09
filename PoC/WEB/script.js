function jQuery (selector, context = document) {
    this.elements = Array.from(context.querySelectorAll(selector));
    return this;
}

jQuery.prototype.each = function(fn) {
    this.elements.forEach((element, index) => fn.call(element, element, index));
    return this;
}

jQuery.prototype.click = function(fn) {
    this.each(element => element.addEventListener('click', fn));
    return this;
}

jQuery.prototype.hide = function() {
    this.each(element => element.style.display = 'none');
    return this;
}

jQuery.prototype.show = function() {
    this.each(element => element.style.display = '');
    return this;
}

jQuery.prototype.mutt = function(att, val) {
    this.each(element => element.setAttribute(att, val));
    return this;
}

const $ = (e) => new jQuery(e);

$('button').click(e => {
    $('button').hide();
    $('audio').mutt('muted', 'muted');
});
