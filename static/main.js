var app = new Vue({
  el: '#app',
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
