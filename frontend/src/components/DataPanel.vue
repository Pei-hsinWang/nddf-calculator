<template>
  <div class="data-panel">
    <el-upload
      ref="uploadRef"
      class="upload-area"
      drag
      :auto-upload="false"
      :show-file-list="false"
      accept=".xlsx,.xls"
      :on-change="handleFileChange"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">
        将Excel文件拖到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">只能上传 xlsx/xls 文件</div>
      </template>
    </el-upload>

    <div v-if="fileInfo" class="file-info">
      <el-descriptions :column="4" border size="small">
        <el-descriptions-item label="文件名">{{ fileInfo.filename }}</el-descriptions-item>
        <el-descriptions-item label="工作簿">
          <el-select 
            v-model="currentSheet" 
            size="small" 
            style="width: 150px"
            @change="handleSheetChange"
          >
            <el-option 
              v-for="sheet in fileInfo.sheets" 
              :key="sheet" 
              :label="sheet" 
              :value="sheet" 
            />
          </el-select>
        </el-descriptions-item>
        <el-descriptions-item label="数据行数">{{ fileInfo.totalRows }}</el-descriptions-item>
        <el-descriptions-item label="列数">{{ fileInfo.columns.length }}</el-descriptions-item>
      </el-descriptions>
    </div>

    <div v-if="previewData.length > 0" class="preview-section">
      <el-divider content-position="left">数据预览 (前10行)</el-divider>
      <el-table :data="previewData" border size="small" max-height="300" style="width: 100%">
        <el-table-column
          v-for="col in previewColumns"
          :key="col"
          :prop="col"
          :label="col"
          min-width="100"
        />
      </el-table>
    </div>

    <div class="action-buttons">
      <el-button
        type="primary"
        size="large"
        :loading="computing"
        :disabled="!rawData.length"
        @click="startCompute"
      >
        <el-icon><Cpu /></el-icon>
        开始计算
      </el-button>
    </div>

    <el-progress
      v-if="computing"
      :percentage="computeProgress"
      :format="progressFormat"
      style="margin-top: 20px"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api'

const props = defineProps({
  config: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['data-loaded', 'compute-complete'])

const uploadRef = ref(null)
const fileInfo = ref(null)
const fileId = ref('')
const currentSheet = ref('')
const previewData = ref([])
const rawData = ref([])
const computing = ref(false)
const computeProgress = ref(0)

const previewColumns = computed(() => {
  if (previewData.value.length > 0) {
    return Object.keys(previewData.value[0])
  }
  return []
})

const handleFileChange = async (uploadFile) => {
  try {
    const result = await api.uploadFile(uploadFile.raw)
    
    fileInfo.value = result
    fileId.value = result.fileId
    currentSheet.value = result.currentSheet
    previewData.value = result.preview
    rawData.value = result.data || result.preview
    
    emit('data-loaded', rawData.value, result.columns)
    ElMessage.success(`文件上传成功，工作簿"${result.currentSheet}"共${result.totalRows}行数据`)
  } catch (error) {
    ElMessage.error('文件解析失败: ' + (error.response?.data?.detail || error.message))
  }
}

const handleSheetChange = async (sheetName) => {
  if (!fileId.value) return
  
  try {
    ElMessage.info(`正在加载工作簿"${sheetName}"...`)
    
    const result = await api.getSheetData(fileId.value, sheetName)
    
    fileInfo.value = {
      ...fileInfo.value,
      currentSheet: sheetName,
      totalRows: result.totalRows,
      columns: result.columns
    }
    previewData.value = result.preview
    rawData.value = result.data
    
    emit('data-loaded', rawData.value, result.columns)
    ElMessage.success(`工作簿"${sheetName}"加载成功，共${result.totalRows}行数据`)
  } catch (error) {
    ElMessage.error('工作簿加载失败: ' + (error.response?.data?.detail || error.message))
  }
}

const startCompute = async () => {
  if (!props.config) {
    ElMessage.warning('请先配置参数')
    return
  }
  
  if (!rawData.value.length) {
    ElMessage.warning('请先上传数据')
    return
  }
  
  computing.value = true
  computeProgress.value = 0
  
  try {
    const progressInterval = setInterval(async () => {
      try {
        const progress = await api.getProgress()
        if (progress.total > 0) {
          computeProgress.value = Math.round((progress.current / progress.total) * 100)
        }
      } catch {
        // ignore
      }
    }, 500)
    
    const result = await api.compute(props.config, rawData.value)
    
    clearInterval(progressInterval)
    computeProgress.value = 100
    
    if (result.success) {
      ElMessage.success(result.message)
      emit('compute-complete', result.results)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('计算失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    computing.value = false
  }
}

const progressFormat = (percentage) => {
  return percentage === 100 ? '完成' : `${percentage}%`
}
</script>

<style scoped>
.data-panel {
  padding: 10px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
}

.file-info {
  margin-top: 20px;
}

.preview-section {
  margin-top: 20px;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

.action-buttons .el-button {
  width: 200px;
}
</style>
