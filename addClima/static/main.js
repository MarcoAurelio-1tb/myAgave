const btn_delete = document.querySelectorAll('.btn-delete')

if(btn_delete){
    const array_delete = Array.from(btn_delete);
    array_delete.forEach((btn) => {
        btn.addEventListener('click', (e) =>{
            if(!confirm('Are you sure about delete it?')) {
                e.preventDefault();
            }
        });
    });
}