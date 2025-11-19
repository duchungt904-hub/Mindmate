// 主 JavaScript 文件
console.log('MindMate 应用已加载');

// 获取存储的 token
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

// 全局 fetch 包装函数（自动携带 token）
window.fetchWithAuth = async (url, options = {}) => {
    const token = getAuthToken();
    
    const headers = {
        ...options.headers
    };
    
    // 添加 Authorization header
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return fetch(url, {
        ...options,
        headers
    });
};

// 向后兼容的函数
window.fetchWithCredentials = window.fetchWithAuth;

// 检查用户认证状态
async function checkAuth() {
    try {
        const response = await fetchWithAuth('/api/auth/check');
        const data = await response.json();
        
        return data.authenticated;
    } catch (error) {
        console.error('检查认证状态失败:', error);
        return false;
    }
}

// 登出函数
window.logout = async function() {
    try {
        await fetchWithAuth('/api/auth/logout', { method: 'POST' });
    } catch (error) {
        console.error('登出失败:', error);
    }
    
    // 清除本地存储
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    
    // 跳转到登录页
    window.location.href = '/login';
};

// 页面加载时的初始化（不再进行冗余的认证检查，后端中间件已处理）
document.addEventListener('DOMContentLoaded', async () => {
    console.log('页面已加载，用户已通过认证');
});
