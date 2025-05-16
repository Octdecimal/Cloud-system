<template>
  <div class="sheet">
    <h2>Node Usage Data</h2>
    <div class="sheet-content">
      <div class="row header">
        <div>Node IP</div>
        <div>CPU Usage</div>
        <div>Memory Usage</div>
      </div>
      <div class="row" v-for="(node, ip) in nodeUsage" :key="ip">
        <div>{{ node.ip }}</div>
        <div>{{ node.cpu_usage }}%</div>
        <div>{{ node.mem_usage }}%</div>
      </div>
    </div>
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
        const response = await fetch('http://172.17.0.2:8000/node_usage');
        const text = await response.text();
        let data = {};
        try {
          data = JSON.parse(text);
        } catch (e) {
          console.error("Failed to parse JSON:", e);
        }
        this.nodeUsage = data;
      } catch (error) {
        console.error("Error fetching node usage:", error);
      }
    }
  },
  mounted() {
    this.fetchNodeUsage();
    setInterval(this.fetchNodeUsage, 1500);
  }
};
</script>

<style scoped>
.sheet {
  padding: 16px;
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  margin: 16px auto;
}

.sheet-content {
  display: flex;
  flex-direction: column;
}

.row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.header {
  font-weight: bold;
  border-bottom: 1px solid #ccc;
  margin-bottom: 8px;
}
</style>