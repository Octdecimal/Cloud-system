<template>
  <div>
    <h3>1. 上傳音檔</h3>
    <label class="file-label">
      選擇音檔
      <input
        type="file"
        accept="audio/*"
        multiple
        @change="onFilesChange"
      />
    </label>

    <!-- 列出已選取的檔案 -->
    <div v-if="files.length" class="selected-list">
      <h4>已選取檔案 ({{ files.length }})：</h4>
      <ul>
        <li v-for="(f, i) in files" :key="i">
          {{ f.name }}
          <button class="remove-btn" @click="removeFile(i)">移除</button>
        </li>
      </ul>
    </div>

    <button
      :disabled="!files.length || uploading"
      @click="upload"
    >
      {{ uploading ? '上傳中…' : '開始上傳' }}
    </button>

    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api.js'

const files = ref([])
const uploading = ref(false)
const message = ref('')
const emit = defineEmits(['uploaded'])

function onFilesChange(e) {
  files.value = Array.from(e.target.files)
}

function removeFile(idx) {
  files.value.splice(idx, 1)
}

async function upload() {
  if (!files.value.length) return

  uploading.value = true
  message.value = ''
  const form = new FormData()
  files.value.forEach(f => form.append('files', f))

  try {
    const res = await api.post('/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    message.value = '✅ 上傳成功！'
    emit('uploaded', res.data.folder)
    files.value = []      // 上傳成功後清空
  }
  catch (e) {
    console.error(e)
    message.value = '❌ 上傳失敗'
  }
  finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.selected-list {
  margin: 8px 0;
}
.selected-list ul {
  padding-left: 20px;
}
.remove-btn {
  margin-left: 8px;
  font-size: 12px;
  color: #c00;
  background: transparent;
  border: none;
  cursor: pointer;
}
.remove-btn:hover {
  text-decoration: underline;
}
.message {
  margin-top: 8px;
}
</style>
