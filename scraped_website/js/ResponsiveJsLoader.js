function ResponsiveJsLoader(buildVer) {
    var dynamicTag=$("[DynamicLoadPath]");
    var url = dynamicTag.attr("DynamicLoadPath");
    //阻塞的方式执行,而非append,避免被异步加载
    document.write('<script type="text/javascript" src="'+url + "&buildVer=" + buildVer+'"><\/script>');
    dynamicTag.remove();
}
ResponsiveJsLoader('v61.30');
console.log('%cresponsive js compile time:2024-10-08 10:39:53','color:#22c1c3;background: rgb(131,58,180);background: linear-gradient(90deg, rgba(131,58,180,1) 0%, rgba(253,29,29,1) 50%,#ff6a00 100%);font-size:20px;')//记录编译时间
