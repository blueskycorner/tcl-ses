<template>
  <div class="login">
    <h1>
      Login
      <amplify-authenticator></amplify-authenticator>
    </h1>
  </div>
</template>

<script>
// import { Auth } from 'aws-amplify'
// import { AmplifyEventBus } from 'aws-amplify-vue'

export default {
  name: 'login',
  data () {
    return {
      msg: 'Welcome to Your Vue.js App'
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
