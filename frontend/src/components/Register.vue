<template>
  <form @submit.prevent="handleSubmit" class="register-form">
    <h2>用户注册</h2>
    
    <div class="form-group">
      <label for="email">邮箱地址</label>
      <input 
        type="email" 
        id="email" 
        v-model="form.email" 
        placeholder="请输入邮箱地址"
        required
      />
    </div>
    
    <div class="form-group">
      <label for="password">密码</label>
      <input 
        type="password" 
        id="password" 
        v-model="form.password" 
        placeholder="请输入密码"
        required
        minlength="6"
      />
    </div>
    
    <div class="form-group">
      <label for="code">验证码</label>
      <div class="code-input-group">
        <input 
          type="text" 
          id="code" 
          v-model="form.code" 
          placeholder="请输入验证码"
          maxlength="4"
          required
        />
        <button 
          type="button" 
          @click="sendVerificationCode" 
          :disabled="countdown > 0"
          class="code-btn"
        >
          {{ countdown > 0 ? `${countdown}秒后重发` : '获取验证码' }}
        </button>
      </div>
    </div>
    
    <button 
      type="submit" 
      class="submit-btn" 
      :disabled="submitting"
    >
      {{ submitting ? '注册中...' : '注册' }}
    </button>
    
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>
    
    <p class="switch-link">
      已有账号？<a href="#" @click.prevent="$emit('switch-to-login')">立即登录</a>
    </p>
  </form>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Register',
  emits: ['switch-to-register'],
  data() {
    return {
      form: {
        email: '',
        password: '',
        code: ''
      },
      submitting: false,
      message: '',
      messageType: '',
      countdown: 0
    }
  },
  methods: {
    async sendVerificationCode() {
      if (!this.form.email) {
        this.showMessage('请输入邮箱地址', 'error')
        return
      }
      
      if (!this.isValidEmail(this.form.email)) {
        this.showMessage('邮箱格式不正确', 'error')
        return
      }
      
      try {
        const response = await axios.post('/api/send-verification-code', {
          email: this.form.email,
          purpose: 'register'
        })
        
        this.showMessage(response.data.message, 'success')
        this.startCountdown()
      } catch (error) {
        this.showMessage(
          error.response?.data?.error || '验证码发送失败，请稍后重试', 
          'error'
        )
      }
    },
    
    async handleSubmit() {
      if (!this.form.email || !this.form.password || !this.form.code) {
        this.showMessage('请填写所有字段', 'error')
        return
      }
      
      if (!this.isValidEmail(this.form.email)) {
        this.showMessage('邮箱格式不正确', 'error')
        return
      }
      
      if (this.form.password.length < 6) {
        this.showMessage('密码长度至少6位', 'error')
        return
      }
      
      if (this.form.code.length !== 4 || !/^\d{4}$/.test(this.form.code)) {
        this.showMessage('请输入4位数字验证码', 'error')
        return
      }
      
      this.submitting = true
      
      try {
        const response = await axios.post('/api/register', this.form)
        this.showMessage(response.data.message, 'success')
        
        // 注册成功后清空表单
        this.form = {
          email: '',
          password: '',
          code: ''
        }
        
        // 3秒后跳转到登录页面
        setTimeout(() => {
          this.$emit('switch-to-login')
        }, 3000)
      } catch (error) {
        this.showMessage(
          error.response?.data?.error || '注册失败，请稍后重试', 
          'error'
        )
      } finally {
        this.submitting = false
      }
    },
    
    isValidEmail(email) {
      const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      return pattern.test(email)
    },
    
    startCountdown() {
      this.countdown = 60
      const timer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    },
    
    showMessage(text, type) {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 5000)
    }
  }
}
</script>

<style scoped>
.register-form {
  width: 100%;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.code-input-group {
  display: flex;
  gap: 10px;
}

.code-input-group input {
  flex: 1;
}

.code-btn {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.code-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.code-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #218838;
}

.submit-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.switch-link {
  text-align: center;
  margin-top: 15px;
  color: #666;
}

.switch-link a {
  color: #007bff;
  text-decoration: none;
}

.switch-link a:hover {
  text-decoration: underline;
}
</style>