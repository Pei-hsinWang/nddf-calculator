<template>
  <div class="app-container">
    <el-card class="header-card">
      <template #header>
        <div class="header">
          <h1>NDDF对偶模型计算工具</h1>
          <p>基于非径向方向距离函数(NDDF)对偶模型的影子价格和边际减排成本计算</p>
        </div>
      </template>
    </el-card>

    <el-row :gutter="20" class="main-content">
      <el-col :span="8">
        <el-card class="config-card">
          <template #header>
            <span><el-icon><Setting /></el-icon> 配置参数</span>
          </template>
          <ConfigForm 
            ref="configFormRef"
            :columns="uploadedColumns"
            @config-change="handleConfigChange"
          />
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="data-card">
          <template #header>
            <div class="data-header">
              <span><el-icon><Upload /></el-icon> 数据上传与计算</span>
            </div>
          </template>
          <DataPanel
            :config="currentConfig"
            @data-loaded="handleDataLoaded"
            @compute-complete="handleComputeComplete"
          />
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="results.length > 0" class="result-card">
      <template #header>
        <div class="result-header">
          <span><el-icon><DataAnalysis /></el-icon> 计算结果</span>
          <el-button type="success" @click="exportResults" :loading="exporting">
            <el-icon><Download /></el-icon> 导出Excel
          </el-button>
        </div>
      </template>
      <ResultTable :results="results" :config="currentConfig" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ConfigForm from './components/ConfigForm.vue'
import DataPanel from './components/DataPanel.vue'
import ResultTable from './components/ResultTable.vue'
import { api } from './api'

const configFormRef = ref(null)
const uploadedColumns = ref([])
const currentConfig = ref(null)
const results = ref([])
const rawData = ref([])
const exporting = ref(false)

const handleConfigChange = (config) => {
  currentConfig.value = config
}

const handleDataLoaded = (data, columns) => {
  rawData.value = data
  uploadedColumns.value = columns
  results.value = []
}

const handleComputeComplete = (computeResults) => {
  results.value = computeResults
}

const exportResults = async () => {
  if (!currentConfig.value || results.value.length === 0) {
    ElMessage.warning('请先完成计算')
    return
  }
  
  exporting.value = true
  try {
    const blob = await api.exportResults(currentConfig.value, results.value)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const mode = currentConfig.value.isVRS ? 'VRS' : 'CRS'
    link.download = `NDDF_ShadowPrices_${mode}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  try {
    const info = await api.getColumnsInfo()
    if (configFormRef.value) {
      configFormRef.value.setDefaultConfig(info.defaultConfig)
    }
  } catch (error) {
    console.error('获取默认配置失败:', error)
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

.app-container {
  max-width: 1600px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 20px;
}

.header {
  text-align: center;
}

.header h1 {
  color: #303133;
  font-size: 28px;
  margin-bottom: 10px;
}

.header p {
  color: #909399;
  font-size: 14px;
}

.main-content {
  margin-bottom: 20px;
}

.config-card, .data-card, .result-card {
  height: fit-content;
}

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-card__header {
  background: #f5f7fa;
  padding: 15px 20px;
}

.el-card__header span {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}
</style>
