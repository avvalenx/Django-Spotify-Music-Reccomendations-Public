$.ajax({
    type: 'get',
    url: '/get_access_token',
    success: function(data) {
        const mydiv = document.getElementById('genres');
        const access = data['access']
        $.ajax({
            url: 'https://api.spotify.com/v1/recommendations/available-genre-seeds',
            type: 'get',
            headers: {'Authorization': 'Bearer ' + access},
            success: function (response) {
                mydiv.innerHTML = "";
                console.log(response);
                for (let a = 0; a < response['genres'].length; a++) {
                    const genre = document.createElement("input");
                    genre.type = 'checkbox';
                    genre.value = response['genres'][a];
                    genre.name = response['genres'][a];

                    const label = document.createElement("label");
                    label.innerHTML = response['genres'][a];

                    mydiv.appendChild(genre);
                    mydiv.appendChild(label);
                };
            },
            error: function (error) {
                if (error['status'] == 401) {
                    $.ajax({
                        type: 'get',
                        url: '/expired_access_token',
                        success: function(data) {
                            getGenres();
                        }
                    });
                }
            }
        });
    },
    error: function (error) {
        console.log(error);
    }
})
