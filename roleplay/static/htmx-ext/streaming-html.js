// Copyright (c) 2024 파이썬사랑방. All rights reserved.

// HTMX Streaming HTML Extension
// 서버에서 스트리밍되는 HTML 응답을 청크 단위로 처리하는 확장
(function () {
  'use strict';
  
  // 상수 정의
  const EXTENSION_NAME = 'streaming-html';
  const HTTP_METHODS = ['get', 'post', 'put', 'delete', 'patch'];
  const DEFAULT_HEADERS = {
    'HX-Request': 'true'
  };
  
  // HTMX API 참조
  let api;
  
  // 활성 요청 추적 (메모리 누수 방지)
  const activeRequests = new WeakMap();
  
  /**
   * HTTP 메서드와 URL을 요소에서 추출
   * @param {HTMLElement} element - 대상 요소
   * @returns {{method: string, url: string}} HTTP 메서드와 URL
   */
  function extractHttpMethodAndUrl(element) {
    let method = 'get';
    let url = element.action || '';
    
    // hx-get, hx-post 등의 속성 확인
    for (const httpMethod of HTTP_METHODS) {
      const attrUrl = element.getAttribute(`hx-${httpMethod}`);
      if (attrUrl) {
        method = httpMethod;
        url = attrUrl;
        break;
      }
    }
    
    return { method, url };
  }
  
  /**
   * Fetch 요청 옵션 생성
   * @param {string} method - HTTP 메서드
   * @param {FormData} formData - 폼 데이터
   * @param {AbortSignal} signal - 취소 시그널
   * @returns {object} Fetch 옵션
   */
  function buildFetchOptions(method, formData, signal) {
    const options = {
      method: method,
      headers: { ...DEFAULT_HEADERS },
      signal: signal
    };
    
    // GET이 아닌 경우 body 추가
    if (method !== 'get') {
      options.body = formData;
    }
    
    return options;
  }
  
  /**
   * GET 요청용 URL 생성 (쿼리 파라미터 추가)
   * @param {string} url - 기본 URL
   * @param {FormData} formData - 폼 데이터
   * @returns {string} 쿼리 파라미터가 추가된 URL
   */
  function buildGetUrl(url, formData) {
    const params = new URLSearchParams(formData);
    const separator = url.includes('?') ? '&' : '?';
    return url + separator + params.toString();
  }
  
  /**
   * 청크 처리 및 DOM 업데이트
   * @param {HTMLElement} element - 소스 요소
   * @param {HTMLElement} targetElement - 대상 요소
   * @param {string} html - HTML 콘텐츠
   * @param {object} swapSpec - 스왑 사양
   */
  function processChunk(element, targetElement, html, swapSpec) {
    // 확장을 통한 응답 변환
    let transformedHtml = html;
    api.withExtensions(targetElement, function (extension) {
      transformedHtml = extension.transformResponse(
        transformedHtml,
        null,
        targetElement
      );
    });
    
    // DOM 업데이트
    api.swap(targetElement, transformedHtml, swapSpec);
  }
  
  /**
   * 스트리밍 에러 처리
   * @param {Error} error - 에러 객체
   * @param {HTMLElement} element - 소스 요소
   */
  function handleStreamingError(error, element) {
    // 기존 콘솔 로깅 유지 (호환성)
    console.error('Streaming Error:', error);
    
    // 선택적 에러 이벤트 발생
    if (element.hasAttribute('hx-streaming-error-event')) {
      htmx.trigger(element, 'streaming-error', { 
        error: error,
        message: error.message 
      });
    }
  }
  
  /**
   * 활성 요청 정리
   * @param {HTMLElement} element - 요소
   */
  function cleanupRequest(element) {
    if (activeRequests.has(element)) {
      activeRequests.delete(element);
    }
  }
  
  /**
   * 스트리밍 요청 시작
   * @param {HTMLElement} element - 소스 요소
   * @param {HTMLElement} targetElement - 대상 요소
   */
  async function startStreaming(element, targetElement) {
    // 기존 요청 취소 (중복 방지)
    if (activeRequests.has(element)) {
      const existingController = activeRequests.get(element);
      existingController.abort();
    }
    
    // 새 AbortController 생성
    const abortController = new AbortController();
    activeRequests.set(element, abortController);
    
    try {
      // HTTP 메서드와 URL 추출
      const { method, url: baseUrl } = extractHttpMethodAndUrl(element);
      
      // 폼 데이터 생성
      const formData = new FormData(element);
      
      // GET 요청인 경우 URL에 파라미터 추가
      const url = method === 'get' 
        ? buildGetUrl(baseUrl, formData)
        : baseUrl;
      
      // Fetch 옵션 생성
      const fetchOptions = buildFetchOptions(
        method, 
        formData, 
        abortController.signal
      );
      
      // 스트리밍 시작 이벤트 (선택적)
      if (element.hasAttribute('hx-streaming-start-event')) {
        htmx.trigger(element, 'streaming-start');
      }
      
      // 요청 시작
      const response = await fetch(url, fetchOptions);
      
      // 응답 검증
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // 스트림 리더 생성
      const reader = response.body.getReader();
      const textDecoder = new TextDecoder();
      let chunkCount = 0;
      
      // 스왑 사양 가져오기
      const swapSpec = api.getSwapSpecification(element);
      
      // 스트림 처리
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          // 스트리밍 완료 이벤트 (선택적)
          if (element.hasAttribute('hx-streaming-complete-event')) {
            htmx.trigger(element, 'streaming-complete', { 
              totalChunks: chunkCount 
            });
          }
          break;
        }
        
        // 청크 디코딩 및 처리
        const responseHtml = textDecoder.decode(value);
        processChunk(element, targetElement, responseHtml, swapSpec);
        
        // 청크 이벤트 발생 (기존 동작 유지)
        htmx.trigger(element, 'chunk', { count: chunkCount++ });
      }
      
    } catch (error) {
      // 취소된 경우는 에러로 처리하지 않음
      if (error.name !== 'AbortError') {
        handleStreamingError(error, element);
      }
    } finally {
      // 요청 정리
      cleanupRequest(element);
    }
  }
  
  // HTMX 확장 정의
  htmx.defineExtension(EXTENSION_NAME, {
    // 초기화
    init: function (apiRef) {
      api = apiRef;
    },
    
    // 이벤트 처리
    onEvent: function (eventName, event) {
      // beforeRequest 이벤트 처리
      if (eventName === 'htmx:beforeRequest') {
        const element = event.target || event.detail.elt;
        
        // streaming-html 확장을 사용하는 요소인지 확인
        if (element.getAttribute('hx-ext') === EXTENSION_NAME) {
          // 기본 HTMX 요청 방지
          event.preventDefault();
          
          // 대상 요소 찾기
          const targetElement = api.getTarget(element);
          
          // 스트리밍 시작
          startStreaming(element, targetElement);
        }
      }
    }
  });
})();