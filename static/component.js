Vue.component('navbar', {
  template: '<div>header</div>'
});

Vue.component('send-tweet', {
  template: `
    <div>
      <p><textarea v-model="status.status"></textarea></p>
      <p><button v-on:click="sendTweet">Tweet</button></p>
    </div>
  `,
  data: function () {
    return {status: {status: ''}}
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

Vue.component('refresh-toggle', {
  template: `
    <div style="position: fixed;bottom: 20px;right: 50px;">
      <button><i class="fa fa-refresh" aria-hidden="true"></i></button>
    </div>
  `
});
