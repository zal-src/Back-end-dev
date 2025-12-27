// โหลด leaderboard จาก localStorage
let leaderboard = JSON.parse(localStorage.getItem('mixOrMatchLeaderboard')) || [];

class AudioController {
    constructor() {
        this.bgMusic = new Audio('Hedwigs Theme Theme from Harry Potter.mp3');
        this.flipSound = new Audio('Assets_Audio_flip.wav');
        this.matchSound = new Audio('Assets_Audio_match.wav');
        this.victorySound = new Audio('Assets_Audio_victory.wav');
        this.gameOverSound = new Audio('defeat-sound.mp3');
        this.bgMusic.volume = 0.5;
        this.bgMusic.loop = true;
    }
    startMusic() {
        this.bgMusic.play();
    }
    stopMusic() {
        this.bgMusic.pause();
        this.bgMusic.currentTime = 0;
    }
    flip() { this.flipSound.play(); }
    match() { this.matchSound.play(); }
    victory() {
        this.stopMusic();
        this.victorySound.play();
    }
    gameOver() {
        this.stopMusic();
        this.gameOverSound.play();
    }
}


class MixOrMatch {
    constructor(totalTime, cards, playerName) {
        this.cardsArray = cards;
        this.totalTime = totalTime;
        this.timeRemaining = totalTime;
        this.timer = document.getElementById('time-remaining');
        this.ticker = document.getElementById('flips');
        this.audioController = new AudioController();
        this.playerName = playerName;
    }

    startGame() {
        this.totalClicks = 0;
        this.timeRemaining = this.totalTime;
        this.cardToCheck = null;
        this.matchedCards = [];
        this.busy = true;

        setTimeout(() => {
            this.audioController.startMusic();
            this.shuffleCards(this.cardsArray);
            this.countdown = this.startCountdown();
            this.busy = false;
        }, 500);

        this.hideCards();
        this.timer.innerText = this.timeRemaining;
        this.ticker.innerText = this.totalClicks;
    }

    startCountdown() {
        return setInterval(() => {
            this.timeRemaining--;
            this.timer.innerText = this.timeRemaining;
            if (this.timeRemaining <= 0) this.gameOver();
        }, 1000);
    }

    gameOver() {
        clearInterval(this.countdown);
        this.audioController.gameOver();
        Swal.fire({
            title: 'Game Over',
            text: 'Better luck next time!',
            icon: 'error',
            confirmButtonColor: '#FF6D00'
        }).then(() => {
            this.showLeaderboard();
        });
    }

    victory() {
        clearInterval(this.countdown);
        this.audioController.victory();
        this.saveScore();
        Swal.fire({
            title: 'Victory!',
            text: `Congratulations ${this.playerName}!`,
            icon: 'success',
            confirmButtonColor: '#FF6D00'
        }).then(() => {
            this.showLeaderboard();
        });
    }

    hideCards() {
        this.cardsArray.forEach(card => card.classList.remove('visible','matched'));
    }

    flipCard(card) {
        if(this.canFlipCard(card)) {
            this.audioController.flip();
            this.totalClicks++;
            this.ticker.innerText = this.totalClicks;
            card.classList.add('visible');

            if(this.cardToCheck) this.checkForCardMatch(card);
            else this.cardToCheck = card;
        }
    }

    checkForCardMatch(card) {
        if(this.getCardType(card) === this.getCardType(this.cardToCheck))
            this.cardMatch(card, this.cardToCheck);
        else
            this.cardMismatch(card, this.cardToCheck);
        this.cardToCheck = null;
    }

    cardMatch(card1, card2) {
        this.matchedCards.push(card1, card2);
        card1.classList.add('matched');
        card2.classList.add('matched');
        this.audioController.match();
        if(this.matchedCards.length === this.cardsArray.length) this.victory();
    }

    cardMismatch(card1, card2) {
        this.busy = true;
        setTimeout(() => {
            card1.classList.remove('visible');
            card2.classList.remove('visible');
            this.busy = false;
        }, 1000);
    }

    shuffleCards(cardsArray) {
        for(let i=cardsArray.length-1;i>0;i--){
            const randIndex = Math.floor(Math.random()*(i+1));
            [cardsArray[i],cardsArray[randIndex]]=[cardsArray[randIndex],cardsArray[i]];
        }
        cardsArray.forEach((card,index)=>card.style.order=index);
    }

    getCardType(card) { return card.getElementsByClassName('card-value')[0].src; }
    canFlipCard(card) { return !this.busy && !this.matchedCards.includes(card) && card!==this.cardToCheck; }

    saveScore() {
        const score = Math.max(0, (this.timeRemaining * 10) - this.totalClicks);
        leaderboard.push({name:this.playerName, score});
        leaderboard.sort((a, b) => b.score - a.score);
        localStorage.setItem('mixOrMatchLeaderboard', JSON.stringify(leaderboard));
    }

    showLeaderboard() {
        const tbody = document.getElementById('leaderboard-list');
        tbody.innerHTML = '';

        // แสดงเฉพาะ Top 5
        leaderboard.slice(0, 5).forEach((player, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${index + 1}</td><td>${player.name}</td><td>${player.score}</td>`;
            tbody.appendChild(tr);
        });

        document.getElementById('leaderboard-overlay').classList.add('visible');
    }
}


// DOM Ready
document.addEventListener('DOMContentLoaded', ()=>{
    const startButton = document.getElementById('start-button');
    const playerNameInput = document.getElementById('player-name-input');
    const playerOverlay = document.getElementById('player-name-overlay');
    const leaderboardRestart = document.getElementById('leaderboard-restart');

    // แทน alert เมื่อผู้เล่นไม่ได้กรอกชื่อ
    startButton.addEventListener('click', ()=>{
        const playerName = playerNameInput.value.trim();
        if(!playerName){
            Swal.fire({
                icon: 'warning',
                title: 'Oops!',
                text: 'Please enter your name before starting!',
                confirmButtonColor: '#FF6D00'
            });
            return;
        }
        playerOverlay.classList.remove('visible');
        const cards = Array.from(document.getElementsByClassName('card'));
        window.game = new MixOrMatch(50, cards, playerName);
        game.startGame();
        playerNameInput.value = "";
    });


    leaderboardRestart.addEventListener('click', ()=>{
        document.getElementById('leaderboard-overlay').classList.remove('visible');
        playerOverlay.classList.add('visible');
    });

    // Card click
    const cards = Array.from(document.getElementsByClassName('card'));
    cards.forEach(card=>card.addEventListener('click', ()=>{if(window.game) window.game.flipCard(card)}));
});

function toggleMenu() {
    const menu = document.getElementById('circle-menu');
 
    if (!menu.classList.contains('show')) {
      // เปิดเมนู
      menu.classList.remove('hide');
      menu.style.display = 'flex';
      setTimeout(() => {
        menu.classList.add('show');
      }, 10);
    } else {
      // ปิดเมนู
      menu.classList.remove('show');
      menu.classList.add('hide');
      setTimeout(() => {
        menu.style.display = 'none';
        menu.classList.remove('hide');
      }, 200); // รอ animation จบ
    }
  }