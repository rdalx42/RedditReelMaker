

const images = [
    "{{ url_for('static', filename='images/display_init/image1.png') }}",
    "{{ url_for('static', filename='images/display_init/image2.jpg') }}",
    "{{ url_for('static', filename='images/display_init/image3.jpg') }}",
    "{{ url_for('static', filename='images/display_init/image4.jpg') }}",
    "{{ url_for('static', filename='images/display_init/image5.jpg') }}",
    "{{ url_for('static', filename='images/display_init/image6.jpg') }}",
    "{{ url_for('static', filename='images/display_init/image7.jpg') }}"
];

const slideshow = document.getElementById("slideshow");

let index = 0;
const fadeDuration = 500;
const minInterval = 5000;
const maxInterval = 50000;

function getRandomFloat(min, max) {
    return Math.random() * (max - min) + min;
}

function changeImage() {
    slideshow.style.opacity = 0;

    setTimeout(() => {
        index = (index + 1) % images.length;
        slideshow.src = images[index];

        slideshow.style.opacity = 1;
    }, fadeDuration);
    setTimeout(changeImage, getRandomFloat(minInterval, maxInterval));
}

setTimeout(changeImage, getRandomFloat(minInterval, maxInterval));
