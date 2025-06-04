<template>
  <div class="container">
    <h1>線上音樂混音平台</h1>
    <div class="card">
      <UploadFiles @uploaded="loadTasks" />
    </div>
    <div class="card" v-if="tasks.length">
      <TaskList :tasks="tasks" @refresh="loadTasks" />
    </div>
    <div v-else class="card" style="text-align:center; color:#999">
      目前尚無任務，請先上傳檔案。
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from './api.js'
import UploadFiles from './components/UploadFiles.vue'
import TaskList    from './components/TaskList.vue'

const tasks = ref([])

async function loadTasks() {
  try {
    const res = await api.get('/status')
    tasks.value = Object.entries(res.data.tasks).map(([id,t])=> ({
      id, status:t.status, node:t.node, result:t.result
    }))
  }
  catch(e){
    console.error(e)
  }
}

onMounted(loadTasks)
</script>
