var store = {
  state: {
    displayTweet: true
  },
  toggleDisplayTweetAction () {
    this.state.displayTweet = !this.state.displayTweet;
  },
};

Vue.component('navbar', {
  template: '<div>header</div>'
});

Vue.component('send-tweet', {
  template: `
    <div v-if="state.displayTweet">
      <p><textarea v-model="status.status"></textarea></p>
      <p><button v-on:click="sendTweet">Tweet</button></p>
    </div>
  `,
  data: function () {
    return {
      status: {status: ''},
      state: store.state,
    }
  },
  methods: {
    sendTweet: function() {
      fetch('/api/statuses/update.json', {
        method: 'POST',
        credentials: 'same-origin',
        headers: new Headers({
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify(this.status)
      })
      .then(r => r.json())
      .catch(e => alert(e))
      .then(r => {
        if (r.id_str) {
          localStorage.setItem(r.id_str, JSON.stringify(r));
          this.status.status = '';
        } else {
          alert(r.errors[0].message);
        }
      });
    }
  },
});

Vue.component('tweet-toggle', {
  template: `
    <div style="position: fixed;bottom: 20px;right: 20px;">
      <button v-on:click="toggleDisplayTweet"><font size="+4">📝</font></button>
    </div>
  `,
  methods: {
    toggleDisplayTweet: () => store.toggleDisplayTweetAction(),
  }
});

Vue.component('refresh-toggle', {
  template: `
    <div style="position: fixed;bottom: 20px;right: 90px;">
      <button><font size="+4">🔄</font></button>
    </div>
  `
});

var app = new Vue({
  el: '#app',
  template: `
    <div>
      <navbar></navbar>
      <send-tweet></send-tweet>
      <tweet-toggle></tweet-toggle>
      <refresh-toggle></refresh-toggle>
    </div>
  `,
  data: {
    displayTweet: false,
    message: 'Hello Vue!'
  },
  methods: {
    toggleDisplayTweet: function() {
      this.displayTweet = !this.displayTweet;
      console.log(this.displayTweet);
    }
  }
});
