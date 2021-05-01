//hide all modals
function hideModals(){
	let modals = document.getElementsByClassName("modal");

	for (modal of modals){
		modal.classList.remove("is-active");
	}
}

//Ensures only specified modal is visible
function showModal(modalid){
	hideModals();
	let visibleModal = document.getElementById(modalid);
	visibleModal.classList.add("is-active");
}

function set_display_balance(amt) {
	balance_container = document.getElementById("acct_balance");
	balance_P = balance_container.getElementsByTagName("p");
	balance_P = balance_P[0];

	prev_bal = balance_P.innerText
	balance_P.innerText = prev_bal.slice(0,4)+amt;
}

function process_sendmoney_response(json_response){
	let alertmsg = ''
	console.log(JSON.stringify(json_response))

	if (json_response['status'] == 'fail') {
		let errmsg = json_response['Error'];
		alertmsg = "Transaction failed.\nError: "+errmsg;
	}
	if (json_response['status'] == 'success') {
		let tx_info = json_response['transaction info']
		let acc_bal = tx_info['source balance']
		acc_bal = acc_bal.toFixed(2);
		alertmsg = "Transaction successful\n\n\n"
		alertmsg += "Amount Sent: "+ tx_info['source currency']+ ' '+tx_info['source amount'].toFixed(2) +'\n'
		alertmsg += "Transaction Fee: "+ "TODO\n"//tx_info[''] + tx_info[''] + '\n' 
		alertmsg += "Account Balance: "+tx_info['source currency']+ ' '+acc_bal
		

		set_display_balance(acc_bal);
	}

	return alertmsg;
}

function sendmoney(){
	//Get Send the filled form to loko
	// console.log("sending money!!!")

	parent_modal = document.getElementById("mod-sendmoney");
	modal_form = parent_modal.getElementsByTagName("form");
	modal_form = modal_form[0];
	// modal_form.submit();

	const formdata = new FormData(modal_form);

	const options = {
		method: 'POST',
		body: formdata,
	};
	url = modal_form.action;

	//TODO:clear password first to avoid inadvertent double send
	inputs = modal_form.getElementsByTagName("input");
	
	for (input of inputs){
		if (input.id == "password") {
			input.value = "";
		}
	}

	// Send request
		fetch(url,options)
		.then(raw_res => raw_res.json())
		.then(json_res => process_sendmoney_response(json_res))
		.then(proc_res => alert(proc_res))

}

hideModals();

//Attach show sendmoney modal event listener to sendmoney btn
let sendmoney_btn = document.getElementById("send-money-btn");
sendmoney_modal_id = "mod-sendmoney";
let showM = showModal.bind(null, sendmoney_modal_id);
sendmoney_btn.addEventListener("click",showM);

//For each modal, add necessary event listeners
let modals = document.getElementsByClassName("modal");

for(modal of modals){
	close_buttons = modal.getElementsByClassName("close-modal");
	for (button of close_buttons){
		button.addEventListener("click",hideModals);
	}

// Add sendmoney() fxn to form submission btn
let send_btn = document.getElementsByClassName("submit-sendmoney");
send_btn = send_btn[0];
send_btn.addEventListener("click", sendmoney);


	// let tablename=modal.getAttribute('id');
	// tablename = tablename.slice("mod-".length);
	// let addE = addEntity.bind(null, tablename);
	// let submit_btn = modal.getElementsByClassName("submit-form");

	// for (btn of submit_btn){
	// 	btn.addEventListener("click", addE);
	// }
}