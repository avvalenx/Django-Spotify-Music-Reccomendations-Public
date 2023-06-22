const csrf_token = document.cookie.slice(10);

function getSongs() {
    $.ajax({
        type: 'get',
        url: '/get_access_token',
        success: function(data) {
            const query = document.getElementById("search").value;
            const mydiv = document.getElementById('songs');
            const access = data['access'];
            $.ajax({
                url: 'https://api.spotify.com/v1/search',
                type: 'get',
                data: {
                    q: query,
                    type: 'track',
                    limit: 10
                },
                headers: {'Authorization': 'Bearer ' + access},
                success: function (response) {
                    mydiv.innerHTML = "";
                    mydiv.className = 'songs';
                    for (let a = 0; a < response['tracks']['items'].length; a++) {
                        const song = document.createElement("input");
                        song.className = 'song'
                        song.type = 'checkbox';
                        song.value = response['tracks']['items'][a]['id'];
                        song.name = response['tracks']['items'][a]['name'];
                        song.class = 'checkbox';
                        song.id = song.value;

                        const song_img = document.createElement("img");
                        song_img.alt = 'album image';
                        song_img.src = response['tracks']['items'][a]['album']['images'][2]['url'];
                        song_img.width = 100;
                        song_img.height = 100;

                        const label = document.createElement("label");
                        label.innerHTML = response['tracks']['items'][a]['artists'][0]['name'] + ": " + response['tracks']['items'][a]['name'];
                        label.htmlFor = song.id;

                        const lineBreak = document.createElement("br");
                        mydiv.append(lineBreak);
                        mydiv.appendChild(song);
                        mydiv.appendChild(label);
                        mydiv.appendChild(song_img)
                    };
                },
                error: function (error) {
                    if (error['status'] == 401) {
                        $.ajax({
                            type: 'get',
                            url: '/expired_access_token',
                            success: function(data) {
                                getSongs();
                            }
                        });
                    } else {
                        $.ajax({
                            type: "POST",
                            url: "/error",
                            headers: {'X-CSRFToken': csrf_token},
                            data: {'error': 'unable to search for songs'},
                        });
                    }
                }
            });
        },
        error: function (error) {
            $.ajax({
                type: "POST",
                url: "/error",
                headers: {'X-CSRFToken': csrf_token},
                data: {'error': 'unable to get access token to search for songs'},
            });
        }
    });
}

$("#submit-button").click(function(e) {
    e.preventDefault();
    var formData = {};
    $("input[name='song']:checked").each(function() {
        formData[this.value] = this.value;
    });
    $.ajax({
        type: "POST",
        url: "/setup",
        headers: {'X-CSRFToken': csrf_token},
        data: formData,
        error: function (error) {
            $.ajax({
                type: "POST",
                url: "/error",
                headers: {'X-CSRFToken': csrf_token},
                data: {'error': 'unable to submit selected songs'},
            });
        }
    });
});