//跳转至注册
$('#register_in').click(function () {
    location.href = "/register/";
});

//注册返回
$('#reg_back').click(function () {
    location.href = "/login/";
});

//点击验证码图片刷新
$('.validcode-img').click(function () {
    $(this)[0].src += "?";
});

//登录提交数据
$('#login_in').on('click',function () {
    // 点击图片后刷新,通过+?的形式实现
    $('.validcode-img')[0].src += "?";
    $.ajax({
        url: "",
        type: 'post',
        headers: {
            // 从cookies里面获取csrftoken,这里要引入jquery.cookie.js文件才能用$.cookie
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data:{
            // 获取并提交登录数据,默认urlencoded格式
            username:$('#username').val(),
            password:$('#password').val(),
            validcode:$('#validcode').val()
        },
        success:function (response) {
            code = response.code;
            $("#login_error").html("");
            if (code==1000){
                // 成功后跳转页面,这里next_url指的是登陆前请求的页面
                location.href = response.next_url
            }else{
                error_msg = response.error_msg;
                $("#login_error").addClass('login-error').html(error_msg);
            }
        }
    })
});

//注册提交数据
$('#reg_commit').click(function () {
    $.ajax({
        url: "",
        type: 'post',
        headers:{
          'X-csrftoken':$.cookie('csrftoken')
        },
        data: {
            username:$('#id_username').val(),
            password:$('#id_password').val(),
            repeat_password:$('#id_repeat_password').val(),
            email:$('#id_email').val(),
            telphone:$('#id_telphone').val(),
        },
        success:function (res) {
            $('.error-tip').html('');
            if (res.code==2000){
                location.href = "/login/"
            }else {
                $.each(res.error_msg, function (key, error) {
                    $('#id_'+key).next('span').html(error[0]).addClass('error-tip');
                })
            }
        }
    })
});

// 左侧菜单栏table切换
// $(".sidebar-menu").on('click', 'li', function () {
//     console.log(111)
// })
// $(".sidebar-menu li").click(function () {
//    console.log( 222)
// })