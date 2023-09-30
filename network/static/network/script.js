function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

document.addEventListener('DOMContentLoaded', function () {
   
    // for new_post error
    if (document.querySelector("#new_post_form") !== null){

        new_post_line = document.querySelector("#new_post")
        new_post_line.addEventListener('input', function(){
            adjustTextareaHeight(this);
        });

        document.querySelector("#new_post_form").onsubmit = (event) => {
            const post = document.querySelector("#new_post").value.trim();
            const button = document.querySelector("#post_button");
            const message = document.querySelector("#post_error_message");
        
            if (post.length <= 0) {
                message.style.display = "block";
                message.innerHTML = "Nothing to Post";
        
                // Prevent the form submission
                event.preventDefault();
                button.disabled = true;
                
    
                // Reset the button to its default state immediately
                setTimeout(() => {
                    button.disabled = false;
                }, 100);
            } 
            else {
                // If the post is not empty, let the form submit as usual
                button.disabled = false;
                message.style.display = "none";
                message.innerHTML = "";
                e_msg = document.querySelector('#error_message')
                e_msg.innerHTML = result["error"]
                e_msg.style.display = "block"
                setInterval(()=>{
                    e_msg.innerHTML =""
                    e_msg.style.display = "none"
                }, 4000)
            }
        };
        
        document.querySelector("#new_post").onkeyup =() =>{
            const post = document.querySelector("#new_post").value.trim();
            if (post.length > 0){
                if (document.querySelector("#post_error_message").style.display ==="block"){
                    document.querySelector("#post_error_message").style.display ="none";
                }
            }
        }
    }
    

    document.querySelectorAll("#edit-post").forEach(function(edit){
            edit.onclick = (event) =>{
                const id = edit.dataset.post

                console.log(id)
                const content = document.querySelector(`#post_content_${id}`)
                const post_con = document.querySelector(`#post_div_${id}`)
                const post_area = document.createElement('textarea')
                const save = document.createElement('button')

                

                post_area.value = content.innerHTML
                post_area.className = "post_edit_line";
                post_area.id = `post_area_${id}`
                post_area.rows =1;
                save.innerHTML = "Save"
                save.className = "edit_post_button"

                post_area.addEventListener('input', function () {
                    adjustTextareaHeight(this);
                });

                post_con.innerHTML = "";
                post_con.append(post_area)
                post_con.append(save)
                

                save.onclick = ()=>{


                    fetch(`/edit_post/${id}`, {
                        method: 'POST',
                        body: JSON.stringify({
                            id: id,
                            content: post_area.value,
                           
                        })
                      })
                      .then(response => response.json())
                      .then(result => {
                        if(result["message"] !== undefined){
                            content.innerHTML = post_area.value
                            post_con.innerHTML = "";
                            post_con.append(content)
                            
                            const s_msg = document.querySelector('#success_message')
                            s_msg.innerHTML = result["message"]
                            s_msg.style.display = "block"
                            setInterval(()=>{
                                s_msg.innerHTML =""
                                s_msg.style.display = "none"
                            }, 4000)
                            
                        }
                        else{
                            post_con.innerHTML = "";
                            post_con.append(content)
                            const e_msg = document.querySelector('#error_message')
                            e_msg.innerHTML = result["error"]
                            e_msg.style.display = "block"
                            setInterval(()=>{
                                e_msg.innerHTML =""
                                e_msg.style.display = "none"
                            }, 4000)
                        }
                        
                      });
                    
                    return false
                }

                event.preventDefault();
            }
    });

    document.querySelectorAll(".img_link img").forEach(function(likeButton) {
        likeButton.onclick = () => {
            const id = likeButton.dataset.post; 
    
            if (likeButton.src.includes("un_liked.png")) {

                fetch(`/likes/${id}`, {
                    method: 'POST',
                    body: JSON.stringify({
                        like_status: true
                       
                    })
                  })
                  .then(response => response.json())
                  .then(result => {
                    if(result["message"] !== undefined){

                        likeButton.classList.remove('unliked')
                        likeButton.classList.add('liked')

                        likeButton.src = "/static/network/images/liked.png";
                        const count = document.querySelector(`#likes_count_${id}`).innerHTML
                        document.querySelector(`#likes_count_${id}`).innerHTML = parseInt(count) +1
                        
                    }
                    else{
                        const e_msg = document.querySelector('#error_message')
                        e_msg.innerHTML = result["error"]
                        e_msg.style.display = "block"
                        setInterval(()=>{
                            e_msg.innerHTML =""
                            e_msg.style.display = "none"
                        }, 4000)
                    }
                    
                  });
            } 
            else if (likeButton.src.includes("liked.png")) {

                fetch(`/likes/${id}`, {
                    method: 'POST',
                    body: JSON.stringify({
                        like_status: false
                        
                    })
                })
                .then(response => response.json())
                .then(result => {
                if(result["message"] !== undefined){
                    likeButton.classList.remove('liked')
                    likeButton.classList.add('unliked')

                    likeButton.src = "/static/network/images/un_liked.png";
                    const count = document.querySelector(`#likes_count_${id}`).innerHTML
                    document.querySelector(`#likes_count_${id}`).innerHTML = parseInt(count) - 1
                    
                }
                else{
                    const e_msg = document.querySelector('#error_message')
                    e_msg.innerHTML = result["error"]
                    e_msg.style.display = "block"
                    setInterval(()=>{
                        e_msg.innerHTML =""
                        e_msg.style.display = "none"
                    }, 4000)
                }
                
                });
            }
        
            return false;
        };
    });

});