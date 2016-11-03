// The following line loads the standalone build of Vue instead of the runtime-only build,
// so you don't have to do: import Vue from 'vue/dist/vue'
// This is done with the browser options. For the config, see package.json
import Vue from 'vue'
import Campgrounds from '../components/campgrounds/campgrounds.vue'
import Router from 'vue-router'
import $ from '../hooks'
Vue.use(Router);

// Define global variables
global.debounce = function (func, wait, immediate) {
    // Returns a function, that, as long as it continues to be invoked, will not
    // be triggered. The function will be called after it stops being called for
    // N milliseconds. If `immediate` is passed, trigger the function on the
    // leading edge, instead of the trailing.
    'use strict';
    var timeout;
    return function () {
        var context = this;
        var args = arguments;
        var later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    }
};

global.$ = $

const routes = [
    {
        path: '/',
        component: {
            render (c) { return c('router-view') }
        },
        children: [
            {path:'dashboard',component: Campgrounds}
        ]
    }
];

const router = new Router({
  'routes' : routes,
  'mode': 'history'
});

new Vue({
  'router':router
}).$mount('#app');