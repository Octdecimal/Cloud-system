<template>
  <div class="file-upload">
    <h2>Upload File</h2>
    <input type="file" multiple @change="handleFileChange" />
    <ul>
      <li v-for="file in selectedFiles" :key="file.name">{{ file.name }}</li>
    </ul>
    <button @click="uploadFile" :disabled="selectedFiles.length === 0">Upload</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedFiles: [],
    };
  },
  methods: {
    handleFileChange(event) {
      this.selectedFiles = Array.from(event.target.files);
    },
    async uploadFile() {
      const formData = new FormData();
      this.selectedFiles.forEach(file => {
        formData.append("files", file); // Append each file
      });

      try {
        const response = await fetch("http://localhost:8000/upload", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          alert("Files uploaded successfully!");
        } else {
          alert("Upload failed.");
        }
      } catch (error) {
        console.error(error);
        alert("An error occurred.");
      }
    },
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
</style>
