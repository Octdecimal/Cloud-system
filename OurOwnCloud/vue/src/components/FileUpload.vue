<template>
  <div class="file-upload">
    <h2>Upload Files</h2>
    <input type="file" multiple @change="handleFileChange" />
    <ul>
      <li v-for="file in selectedFiles" :key="file.name">{{ file.name }}</li>
    </ul>
    <button @click="uploadFile" :disabled="selectedFiles.length === 0">Upload</button>

    <hr />

    <h2>Task Queue</h2>
    <button @click="fetchTasks()">Refresh</button>
    <table>
      <thead>
        <tr>
          <th>Task ID</th>
          <th>Status</th>
          <th>Node</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(task, taskId) in taskQueue" :key="taskId">
          <td>{{ taskId }}</td>
          <td>{{ task.status }}</td>
          <td>{{ task.node || '—' }}</td>
          <td>
            <button v-if="task.status === 'waiting'" @click="removeTask(taskId)">
              Remove
            </button>
            <button v-if="task.status === 'done' && task.result" @click="downloadResult(task.result)">
              Download
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedFiles: [],
      taskQueue: {},
    };
  },
  methods: {
    handleFileChange(event) {
      this.selectedFiles = Array.from(event.target.files);
    },
    async uploadFile() {
      const formData = new FormData();
      this.selectedFiles.forEach(file => {
        formData.append("files", file);
      });

      try {
        const response = await fetch("http://localhost:8000/upload", {
          method: "POST",
          body: formData,
        });

        const result = await response.json();
        
        if (response.ok && result.message) {
          alert(result.message);
          formData.delete("files");
          this.selectedFiles = [];
          this.fetchTasks();
        } else {
          console.warn("Unexpected response structure:", result);
          alert(result.error || "An unexpected error occurred.");
        }

      } catch (error) {
        console.error("Error during upload:", error);
        alert("An error occurred during upload.");
      }
    },
    async fetchTasks() {
      try {
        const response = await fetch("http://localhost:8000/status");
        if (!response.ok) {
          console.error(`Failed to load task status. Status: ${response.status}`);
          alert(`Failed to load task status. Status: ${response.status}`);
          return;
        }

        const data = await response.json();
        this.taskQueue = data.tasks || {};
      } catch (error) {
        console.error("Error fetching task status:", error);
        alert("Failed to load task status.");
      }
    },
    async removeTask(taskId) {
      try {
        const response = await fetch(`http://localhost:8000/remove/${taskId}`, {
          method: "DELETE",
        });

        if (response.ok) {
          alert("Task removed successfully.");
          this.fetchTasks();
        } else {
          console.error(`Failed to remove task. Status: ${response.status}`);
          alert(`Failed to remove task. Status: ${response.status}`);
        }
      } catch (error) {
        console.error("Error removing task:", error);
        alert("Failed to remove task.");
      }
    },
    async downloadResult(filePath) {
      // 假設你有設計一個 /download API 提供檔案下載
      const url = `http://localhost:8000${filePath}`;
      window.open(url, "_blank");
    },
  },
  mounted() {
    this.fetchTasks();
  },
};
</script>

<style scoped>
.file-upload {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

button {
  padding: 6px 14px;
  font-size: 14px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  border: 1px solid #ccc;
  padding: 6px;
  text-align: center;
}
</style>
