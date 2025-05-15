<template>
  <div class="p-4">
    <h1 class="text-xl font-bold mb-4">Node Usage Data</h1>
    <table class="w-full bg-white shadow rounded-lg">
      <thead>
        <tr>
          <th class="p-2 border-b">Node IP</th>
          <th class="p-2 border-b">CPU Usage</th>
          <th class="p-2 border-b">Memory Usage</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(node, ip) in nodeUsage" :key="ip">
          <td class="p-2 border-b">{{ ip }}</td>
          <td class="p-2 border-b">{{ node[0] || 'N/A' }}</td>
          <td class="p-2 border-b">{{ node[1] || 'N/A' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      nodeUsage: {}
    };
  },
  methods: {
    async fetchNodeUsage() {
      try {
        const response = await fetch('http:172.17.0.2:8000/node_usage');
        const data = await response.json();
        this.nodeUsage = data;
      } catch (error) {
        console.error("Error fetching node usage:", error);
      }
    }
  },
  mounted() {
    this.fetchNodeUsage();
    setInterval(this.fetchNodeUsage, 5000);
  }
};
</script>

<style scoped>
.table {
  width: 100%;
  border-collapse: collapse;
}
.table th, .table td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}
</style>
