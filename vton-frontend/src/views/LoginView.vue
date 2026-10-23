<template>
    <div class="login-container">
        <el-card class="login-card">
            <h2>用户登录</h2>
            <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="80px">
                <el-form-item label="账号" prop="account">
                    <el-input v-model="loginForm.account" placeholder="请输入邮箱或手机号" />
                </el-form-item>
                <el-form-item label="密码" prop="password">
                    <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="handleLogin" :loading="loginLoading"
                        style="width: 100%">登录</el-button>
                </el-form-item>
                <el-form-item>
                    <p class="register-link">没有账号？<a href="/register">立即注册</a></p>
                </el-form-item>
            </el-form>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElLoading } from 'element-plus';
import { usersAPI } from '../api';
import type { LoginTokenResponse } from '@/types/user';
import { useUserStore } from '@/stores/userStore'

const router = useRouter();
const userStore = useUserStore()

// 登录表单
const loginForm = reactive({
    account: '',
    password: ''
});

// 表单验证规则
const loginRules = reactive({
    account: [
        { required: true, message: '请输入账号', trigger: 'blur' },
        {
            validator: (rule: any, value: string, callback: any) => {
                // 验证邮箱或手机号格式
                const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
                const phoneRegex = /^1[3-9]\d{9}$/;
                if (!emailRegex.test(value) && !phoneRegex.test(value)) {
                    callback(new Error('请输入有效的邮箱或手机号'));
                } else {
                    callback();
                }
            },
            trigger: 'blur'
        }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 5, max: 20, message: '密码长度在 5 到 20 个字符', trigger: 'blur' }
    ]
});

// 表单引用
const loginFormRef = ref();

// 加载状态
const loginLoading = ref(false);

// 登录
const handleLogin = () => {
    if (!loginFormRef.value) return;

    loginFormRef.value.validate((valid: boolean) => {
        if (valid) {
            const loading = ElLoading.service({
                lock: true,
                text: '正在登录...',
                background: 'rgba(0, 0, 0, 0.7)'
            });

            usersAPI.loginUser({
                account: loginForm.account,
                password: loginForm.password
            }).then((data: LoginTokenResponse) => {
                ElMessage.success('登录成功！');
                // 使用 store 设置登录状态
                userStore.setLoginStatus(true, data.access_token);
                router.push('/');
            }).catch(() => {
                ElMessage.error('登录失败，请检查账号或密码是否正确');
            }).finally(() => {
                loading.close();
            });
        } else {
            ElMessage.error('请检查表单信息');
        }
    });
};
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 60px);
    background-color: #f5f7fa;
}

.login-card {
    width: 500px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-card h2 {
    text-align: center;
    margin-bottom: 20px;
    color: #303133;
}

.register-link {
    text-align: center;
    margin: 0;
}

.register-link a {
    color: #409eff;
    text-decoration: none;
}

.register-link a:hover {
    text-decoration: underline;
}
</style>