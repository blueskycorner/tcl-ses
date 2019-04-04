<template>
  <div class="login">
    <h1>
      TCL
    </h1>
    <div v-if="!image">
      <h2>Select an image</h2>
      <input type="file" @change="onFileChange">
    </div>
    <div v-else>
      <img :src="image" />
      <button @click="removeImage">Remove image</button>
      <button @click="uploadImage">Upload image</button>
    </div>
    <div v-if="end">
      <h2>OK: {{ok}}</h2>
    </div>
    <amplify-sign-out></amplify-sign-out>
  </div>
</template>

<script>
import axios from 'axios'
// import { Auth } from 'aws-amplify'
// import { AmplifyEventBus } from 'aws-amplify-vue'

export default {
  name: 'login',
  data () {
    return {
      image: '',
      filename: '',
      end: false,
      ok: ''
    }
  },
  methods: {
    onFileChange (e) {
      let files = e.target.files || e.dataTransfer.files
      if (!files.length) return
      this.createImage(files[0])
    },
    createImage (file) {
      // var image = new Image()
      let reader = new FileReader()
      reader.onload = (e) => {
        console.log('length: ', e.target.result.includes('data:image/jpeg'))
        if (!e.target.result.includes('data:image/jpeg')) {
          return alert('Wrong file type - JPG only.')
        }
        this.image = e.target.result
        this.filename = file.name
      }
      reader.readAsDataURL(file)
    },
    removeImage: function (e) {
      console.log('Remove clicked')
      this.image = ''
      this.filename = ''
      this.end = false
      this.ok = ''
    },
    uploadImage: async function (e) {
      console.log('Upload clicked')
      console.log('filename: ' + this.filename)

      const jwt = this.$store.state.user
        .getSignInUserSession()
        .getIdToken()
        .getJwtToken()

      // this.uploadOngoing = true
      // Get the presigned URL
      const response = await axios({
        method: 'GET',
        headers: { 'Authorization': jwt },
        params: {
          filename: this.filename
        },
        // url: `https://c60esxid12.execute-api.us-east-1.amazonaws.com/dev/buildSignedUrlUpload`
        url: `https://o7b2gdvqsd.execute-api.us-east-1.amazonaws.com/prod/buildSignedUrlUpload`
      })

      console.log('Response: ', response.data)
      console.log('Uploading: ', this.image)

      let binary = atob(this.image.split(',')[1])
      let array = []
      for (var i = 0; i < binary.length; i++) {
        array.push(binary.charCodeAt(i))
      }
      let blobData = new Blob([new Uint8Array(array)])
      console.log('Uploading to: ', response.data.signedUrlUpload)
      const result = await fetch(response.data.signedUrlUpload, {
        method: 'PUT',
        headers: {},
        body: blobData
      })
      console.log('Result: ', result)
      this.end = true
      this.ok = result.ok
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
#app {
  text-align: center;
}
img {
  width: 30%;
  margin: auto;
  display: block;
  margin-bottom: 10px;
}
button {
}
</style>
