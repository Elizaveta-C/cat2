$(document).ready(function(){

    $('#register-form').on('submit', function(e){
        e.preventDefault(); 
        
        let err = 0;
        let password = $('#password').val().trim();
        let confirmPassword = $('#confirm_password').val().trim();
        let fullname = $('#fullname').val().trim();

        
        if (fullname === '' || password !== confirmPassword){
            err = 1;
            alert('Пожалуйста, заполните имя или проверьте совпадение паролей!');
        }

        if (err === 0){
            $.ajax({
                url: '/user_register',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    name: fullname,
                    email: $('#email').val().trim(),
                    password: password
                })
            })
            .done(function(data){
                if (data.result){
                    alert('Регистрация успешна!');
                    window.location.href = '/login'; 
                } else {
                    alert(data.error || 'Что-то пошло не так при регистрации');
                }
            })
            .fail(function(xhr){
                let response = xhr.responseJSON;
                alert(response && response.error ? response.error : 'Ошибка сервера при регистрации');
            });
        }
    });

    
    $('#login-form').on('submit', function(e){
        e.preventDefault(); 
        
        $.ajax({
            url: '/user_login',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                email: $('#username').val().trim(), 
                password: $('#password').val().trim()
            })
        })
        .done(function(data){
            if (data.result){
                alert('Вы успешно вошли!');
                window.location.href = '/dashboard';
            } else {
                alert(data.error || 'Неверный логин или пароль');
            }
        })
        .fail(function(xhr){
            let response = xhr.responseJSON;
            alert(response && response.error ? response.error : 'Неверная почта или пароль');
        });
    });

});
