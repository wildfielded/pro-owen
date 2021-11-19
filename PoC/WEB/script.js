//----- Наколенный нановариант jQuery -----
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

const $ = (e) => new jQuery(e);

//----- Всё остальное -----

// loopPlaying=false - звуковой файл проигрывается один раз при загрузке страницы
// loopPlaying=true - если нужна бесконечная сирена, пока оператор не нажмёт кнопку
const loopPlaying = true;
let newTrouble = document.getElementById('newalarm');

HTMLAudioElement.prototype.stop = function() {
    this.pause();
    this.currentTime = 0.0;
}

if (newTrouble !== null) {
    let playSound = new Audio('sirena.wav');
    if (loopPlaying) {
        if (typeof playSound.loop == 'boolean') {
            playSound.loop = true;
        } else {
            playSound.addEventListener('onended', function() {
                this.currentTime = 0.0;
                this.play();
                this.muted = false;
            }, false);
        }
        playSound.play();
        $('button').click(e => {
            $('button').hide();
            playSound.stop();
        });
    } else {
        $('button').hide();
        playSound.play();
    }
}
