class StarRating extends HTMLElement {
    get value () {
        return this.getAttribute('value') || 0;
    }

    set value (val) {
        this.setAttribute('value', val);
        this.highlight(this.value - 1);
    }

    get number () {
        return this.getAttribute('number') || 5;
    }

    set number (val) {
        this.setAttribute('number', val);

        this.stars = [];

        while (this.firstChild) {
            this.removeChild(this.firstChild);
        }

        for (let i = 0; i < this.number; i++) {
            let s = document.createElement('div');
            s.className = 'star';
            this.appendChild(s);
            this.stars.push(s);
        }

        this.value = this.value;
    }

    highlight (index) {
        this.stars.forEach((star, i) => {
            star.classList.toggle('full', i <= index);
        });
    }

    constructor () {
        super();

        this.number = this.number;

        this.addEventListener('mousemove', e => {
            let box = this.getBoundingClientRect(),
                starIndex = Math.floor((e.pageX - box.left) / box.width * this.stars.length);

            this.highlight(starIndex);
        });

        this.addEventListener('mouseout', () => {
            this.value = this.value;
            console.log(this.value);
            console.log(getcurrent);
        });

        this.addEventListener('click', e => {
            let box = this.getBoundingClientRect(),
                starIndex = Math.floor((e.pageX - box.left) / box.width * this.stars.length);

            this.value = starIndex + 1;

            let rateEvent = new Event('rate');
            this.dispatchEvent(rateEvent);

            $.post('', {'action': 'rate', 'rating': this.value}, function() {
              Msgs.add_msg('Rating Updated ! Thank you for the input.',  'info');
            })
        });

        var getcurrent = $('.get-app-stars').text()
        console.log(getcurrent);

        if (getcurrent == 0){
            // pass
        } else if(getcurrent > 0 && getcurrent < 20) {
            this.value = 1;
            this.highlight(0);
        } else if(getcurrent >= 20 && getcurrent < 40) {
            this.value = 2;
            this.highlight(1);
        } else if(getcurrent >= 40 && getcurrent < 60) {
            this.value = 3;
            this.highlight(2);
        } else if(getcurrent >= 60 && getcurrent < 80) {
            this.value = 4;
            this.highlight(3);
        } else {
            this.value = 5;
            this.highlight(4);
        }
    }
}

customElements.define('x-star-rating', StarRating);