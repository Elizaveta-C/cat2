$(document).ready(function(){
    // 1. Обработка регистрации
    $('#67').on('submit', function(e){
        e.preventDefault();
        var name = $('#fullname').val().trim();
        var email = $('#email').val().trim();
        var pass = $('#password').val().trim();
        var confirmPass = $('#confirm_password').val().trim();

        if (name === '' || email === '' || pass === '' || pass !== confirmPass) {
            alert('Заполните все поля и убедитесь, что пароли совпадают!');
            return;
        }

        $.ajax({
            url: '/api/user_register',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                name: name,
                password: pass,
                email: email
            })
        }).done(function(res){
            if (res.error) {
                alert('Ошибка: ' + res.error);
            } else {
                alert('Регистрация прошла успешно! Сейчас откроется страница входа.');
                window.location.href = '/login';
            }
        }).fail(function(){
            alert('Ошибка соединения с сервером');
        });
    });

    // 2. Обработка входа в аккаунт
    $('#login-form').on('submit', function(e){
        e.preventDefault();
        $.ajax({
            url: '/api/login',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                email: $('#username').val(),
                password: $('#password').val()
            })
        }).done(function(res){
            if (res.error) {
                alert('Ошибка: ' + res.error);
            } else {
                window.location.href = '/profile';
            }
        }).fail(function(){
            alert('Ошибка соединения с сервером');
        });
    });

    // 3. Обработка чата с нейросетью в профиле
    $('#chat-form').on('submit', function (e) {
        e.preventDefault();
        var text = $('#chat-input').val().trim();
        if (!text) return;

        var $msgs = $('#chat-messages');
        var $btn = $(this).find('button[type="submit"]');

        $msgs.append($('<div class="msg user"></div>').text(text));
        $('#chat-input').val('').prop('disabled', true);
        $btn.prop('disabled', true).text('Думаю...');
        $msgs.scrollTop($msgs[0].scrollHeight);

        $.ajax({
            url: '/api/chat',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: text })
        }).done(function (res) {
            if (res.reply) {
                $msgs.append($('<div class="msg bot"></div>').text(res.reply));
            } else {
                $msgs.append($('<div class="msg bot"></div>').text('Ошибка: ' + (res.error || 'нет ответа')));
            }
        }).fail(function () {
            $msgs.append($('<div class="msg bot"></div>').text('Ошибка: сервер не отвечает'));
        }).always(function () {
            $('#chat-input').prop('disabled', false).focus();
            $btn.prop('disabled', false).text('Отправить');
            $msgs.scrollTop($msgs[0].scrollHeight);
        });
    });

    // Отправка сообщения по нажатию Enter (Shift + Enter для новой строки)
    $('#chat-input').on('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            $('#chat-form').submit();
        }
    });
});
