
function check_form_oracle(p_action){


    var check_count = 0
    var v_action = p_action;

     var inputElements = document.getElementsByName('lst_servers')
    for(var i=0; inputElements[i]; ++i){
      if(inputElements[i].checked){
         check_count = check_count + 1
      }}


    if (document.Oracle.v_oracle_user.value.length == 0) {
        alert('Please, inform the Oracle User')
         document.Oracle.v_oracle_user.focus()
    }
    else if (document.Oracle.v_oracle_password.value.length == 0) {
        alert('Please, inform the Oracle Password')
         document.Oracle.Oracle_senha.focus()
    }
    else if (check_count == 1){
        alert('Please, check at least one server')
     }
     else{
            return v_action
    }
}



function check_form(){

    var check_count = 0
     var v_action = document.Oracle.v_action.value;
     var inputElements = document.getElementsByName('lst_servers')
    for(var i=0; inputElements[i]; ++i){
      if(inputElements[i].checked){
         check_count = check_count + 1
      }}


    if (document.Oracle.v_oracle_user.value.length == 0) {
         alert('Please, inform the Oracle User')
         document.Oracle.v_oracle_user.focus()
    }
    else if (document.Oracle.v_oracle_password.value.length == 0) {
         alert('Please, inform the Oracle Password')
         document.Oracle.v_oracle_password.focus()
    }
    else if (check_count == 1){
         alert('Please, check at least one server')
     }

     else if (document.Oracle.v_sql_file.value.length == 0 && (v_action == 1 || v_action == 2)) {
        if (v_action == 1){
            alert('Please, inform sql file.')
        } else if (v_action == 2){
            alert('Please, inform csv file.')
        }
         document.Oracle.v_sql_file.focus()
    }

   else  if (document.Oracle.v_csv_splitter.value.length == 0 && (v_action == 0 || v_action == 2)) {
        alert('Please, inform the column splitter.')
         document.Oracle.v_csv_splitter.focus()
    }

        else if (document.Oracle.v_sql_query.value.length == 0 && v_action == 0) {
        alert('Please, inform the sql query.')
         document.Oracle.v_sql_query.focus()
    }

    else  if (document.Oracle.v_path_export.value.length == 0 && v_action == 0) {
        alert('Please, inform the destination path.')
         document.Oracle.v_path_export.focus()
    }

    else  if (document.Oracle.v_sql_loader_owner.value.length == 0 && v_action == 2) {
        alert('Please, inform the owner table.')
         document.Oracle.v_sql_loader_owner.focus()
    }

    else  if (document.Oracle.v_sql_loader_table.value.length == 0 && v_action == 2) {
        alert('Please, inform the table name.')
         document.Oracle.v_sql_loader_table.focus()
    }
    else{
        document.Oracle.submit();
    }

}
