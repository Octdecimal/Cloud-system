<template>
  <div id="app">
    <header>
      <h1>Distributed Computing Dashboard</h1>
    </header>
    <main class="content">
      <section class="upload-panel">
        <FileUpload />
      </section>
      <!-- Add panels here later for TaskQueue, NodeStatus, etc -->
    </main>
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
  color: #2c3e50;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 30px;
}

.content {
  display: flex;
  justify-content: center;
  gap: 40px;
  flex-wrap: wrap;
}

.upload-panel {
  flex: 1 1 300px;
  max-width: 400px;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
</style>
