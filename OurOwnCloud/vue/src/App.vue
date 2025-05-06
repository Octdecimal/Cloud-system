<template>
  <div id="app">
    <h1>Distributed Computing Dashboard</h1>
    <FileUpload />
    <!-- You can later add TaskQueue and NodeStatus components here -->
  </div>
</template>

<script>
import FileUpload from './components/FileUpload.vue';

export default {
  components: {
    FileUpload,
  },
};
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
}
</style>
