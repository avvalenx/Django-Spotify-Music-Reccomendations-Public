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
                    console.log(response);
                    for (let a = 0; a < response['tracks']['items'].length; a++) {
                        const song = document.createElement("input");
                        song.type = 'checkbox';
                        song.value = response['tracks']['items'][a]['id'];
                        song.name = response['tracks']['items'][a]['name'];
                        song.class = 'checkbox';

                        const label = document.createElement("label");
                        label.innerHTML = response['tracks']['items'][a]['name'];

                        mydiv.appendChild(song);
                        mydiv.appendChild(label);
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
                    }
                }
            });
        },
        error: function (error) {
            console.log(error);
        }
    });
}

const csrf_token = document.cookie.slice(10);

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
        success: function(data) {
            console.log(data);
        }
    });
});