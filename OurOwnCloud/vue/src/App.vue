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

</style>
