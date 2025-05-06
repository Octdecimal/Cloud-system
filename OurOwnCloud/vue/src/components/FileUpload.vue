<!-- src/components/FileUpload.vue -->
<template>
  <div class="file-upload">
    <h2>Upload File</h2>
    <input type="file" @change="handleFileChange" />
    <button @click="uploadFile" :disabled="!selectedFile">Upload</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedFile: null,
    };
  },
  methods: {
    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
    },
    async uploadFile() {
      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        const response = await fetch('http://localhost:8000/upload', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          alert('File uploaded successfully!');
        } else {
          alert('Upload failed.');
        }
      } catch (error) {
        console.error(error);
        alert('An error occurred.');
      }
    },
  },
};
</script>

<style scoped>
.file-upload {
  margin: 20px;
}
</style>
