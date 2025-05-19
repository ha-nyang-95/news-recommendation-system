import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const newsService = {
    // 검색 API
    async search(params) {
        try {
            const response = await axios.get(`${API_BASE_URL}/news/search/`, { params });
            return response.data;
        } catch (error) {
            console.error('검색 중 오류 발생:', error);
            throw error;
        }
    },

    // 검색어 추천 API
    async suggest(query) {
        try {
            const response = await axios.get(`${API_BASE_URL}/news/suggest/`, {
                params: { q: query }
            });
            return response.data;
        } catch (error) {
            console.error('추천 검색어 조회 중 오류 발생:', error);
            throw error;
        }
    },

    // 연관 키워드 API
    async getRelatedKeywords(query) {
        try {
            const response = await axios.get(`${API_BASE_URL}/news/related-keywords/`, {
                params: { q: query }
            });
            return response.data;
        } catch (error) {
            console.error('연관 키워드 조회 중 오류 발생:', error);
            throw error;
        }
    },

    // 조회수 증가 API
    async incrementView(articleId) {
        try {
            const response = await axios.post(`${API_BASE_URL}/news/${articleId}/increment_view/`);
            return response.data;
        } catch (error) {
            console.error('조회수 증가 중 오류 발생:', error);
            throw error;
        }
    },

    // 추천 기사 API
    async getRecommendedArticles(articleId) {
        try {
            const response = await axios.get(`${API_BASE_URL}/news/${articleId}/recommend/`);
            return response.data;
        } catch (error) {
            console.error('추천 기사 조회 중 오류 발생:', error);
            throw error;
        }
    }
}; 