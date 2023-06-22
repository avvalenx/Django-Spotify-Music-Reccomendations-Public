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
                for (let a = 0; a < response['genres'].length; a++) {
                    const genre = document.createElement("input");
                    genre.type = 'checkbox';
                    genre.value = response['genres'][a];
                    genre.name = response['genres'][a];
                    genre.class = 'checkbox';
                    genre.id = genre.value;

                    const label = document.createElement("label");
                    label.innerHTML = response['genres'][a];
                    label.htmlFor = genre.id;

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
                } else {
                    $.ajax({
                        type: "POST",
                        url: "/error",
                        headers: {'X-CSRFToken': csrf_token},
                        data: {'error': 'unable to get genres'},
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
            data: {'error': 'unable to get access token to search for genres'},
        });
    }
})
