<template>
  <div class="data-use-panel">
    <h1>Data Use</h1>
    <ul>
      <li v-for="(node, ip) in nodes" :key="ip">
        <strong>{{ ip }}</strong>: CPU Usage - {{ node[0] }}%, Memory Usage - {{ node[1] }}%
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';

export default {
  name: 'DataUse',
  setup() {
    const nodes = ref({});
    let intervalId = null;

    const fetchNodes = () => {
      // Example API call. Replace with actual server call.
      fetch('http://172.17.0.2:8000/node_usage')
        .then((response) => response.json())
        .then((data) => {
          nodes.value = data;
        })
        .catch((error) => console.error('Error fetching node data:', error));
    };

    onMounted(() => {
      fetchNodes();
      intervalId = setInterval(fetchNodes, 5000);
    });

    onBeforeUnmount(() => {
      clearInterval(intervalId);
    });

    return {
      nodes
    };
  }
};
</script>

<style scoped>
.data-use-panel {
  flex: 1 1 300px;
  max-width: 400px;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  background-color: #f9f9f9;
}
</style>
