let allRecords = [];
let matchedRecords = [];

let table = null;

/* charts */
let chart = null;
let barChart = null;
let hiddenGroups = new Set();
let barLabels = [];
let IntExpenseChart = null;

let selectedSet = new Set();

const groupColors = {};

const palette = [
	"#2563eb",
"#16a34a",
"#dc2626",
"#9333ea",
"#f59e0b",
"#0891b2",
"#ea580c",
"#4f46e5"
];

/* ===================== COLOR ===================== */

function getColor(group){
	
	group = group || "Ungrouped";
	
	if(!groupColors[group]){
		
		groupColors[group] =
		palette[
			Object.keys(groupColors).length %
			palette.length
		];
	}
	
	return groupColors[group];
}

/* ===================== SUMMARY ===================== */

function renderSummary(s = {}){
	
	const expenseRatio =
	s.net_income
	? (s.net_expense / s.net_income) * 100
	: 0;
	
	const savingsRatio =
	s.net_income
	? (s.saved / s.net_income) * 100
	: 0;
	
	/* avg expense / transaction */
	
	const avgPerTxn =
	s.transaction_count
	? Number(s.net_expense || 0) /
	Number(s.transaction_count)
	: 0;
	
	/* avg expense / day */
	
	const uniqueDays = new Set(
		allRecords.map(r => r.date)
	).size;
	
	const totalExpense = allRecords.reduce(
		(sum, r) =>
		sum + Number(r.amt || 0),
										   0
	);
	
	const avgPerDay =
	uniqueDays
	? totalExpense / uniqueDays
	: 0;
	
	document.getElementById(
		"summaryGrid"
	).innerHTML = `
	
	<div class="card income">
	<h4>💰 Total Incoming</h4>
	<p>₹${Number(
		s.total_incoming || 0
	).toFixed(2)}</p>
	</div>
	
	<div class="card expense">
	<h4>💸 Total Outgoing</h4>
	<p>₹${Number(
		s.total_outgoing || 0
	).toFixed(2)}</p>
	</div>
	
	<div class="card expense">
	<h4>📉 Net Expense</h4>
	<p>₹${Number(
		s.net_expense || 0
	).toFixed(2)}</p>
	</div>
	
	<div class="card income">
	<h4>📈 Net Income</h4>
	<p>₹${Number(
		s.net_income || 0
	).toFixed(2)}</p>
	</div>
	
	<div class="card savings">
	<h4>🏦 Saved</h4>
	<p>₹${Number(
		s.saved || 0
	).toFixed(2)}</p>
	</div>
	
	<div class="card">
	<h4>💳 Current Balance</h4>
	<p>₹${Number(
		s.current_balance || 0
	).toFixed(2)}</p>
	</div>
	
	<div class="card">
	<h4>📊 Expense Ratio</h4>
	<p>${expenseRatio.toFixed(1)}%</p>
	</div>
	
	<div class="card">
	<h4>📊 Savings Ratio</h4>
	<p>${savingsRatio.toFixed(1)}%</p>
	</div>
	
	<div class="card">
	<h4>🔁 Reimbursed</h4>
	<p>₹${Number(
		s.reimbursed || 0
	).toFixed(2)}</p>
	</div>
	
	<div class="card">
	<h4>🧾 Transactions</h4>
	<p>${s.transaction_count || 0}</p>
	</div>
	
	<div class="card">
	<h4>📌 Avg Exp/Trans.</h4>
	<p>₹${avgPerTxn.toFixed(2)}</p>
	</div>
	
	<div class="card">
	<h4>📅 Avg Exp/Day</h4>
	<p>₹${avgPerDay.toFixed(2)}</p>
	</div>
	`;
}

/* ===================== TABLE ===================== */

function initTable(records){
	
	if(table){
		
		table.destroy();
		
		$("#expenseTable tbody").empty();
	}
	
	table = $("#expenseTable").DataTable({
		
		data: records,
		
		destroy: true,
		
		columns: [
			
			{
				data: "id",
				
				render: id => `
				<input
				type="checkbox"
				data-id="${id}"
				>
				`
			},
			
			{ data: "date" },
			
			{ data: "paid_to" },
			
			{ data: "notes" },
			
			{
				data: "amt",
				
				render: function(data, type){
					
					const val =
					Number(data || 0);
					
					if(type === "display"){
						return `₹${val.toFixed(2)}`;
					}
					
					return val;
				},
				
				type: "num"
			},
			
			{ data: "bal" },
			
			{
				data: "group",
				
				render: g => `
				<span
				class="group-badge"
				style="background:${getColor(g)}">
				${g || "Ungrouped"}
				</span>
				`
			}
		],
		
		pageLength: 25,
		
		order: [[1, "desc"]]
	});
	
	/* checkbox tracking */
	
	$("#expenseTable tbody").on(
		"change",
		"input[type=checkbox]",
		function(){
			
			const id =
			$(this).data("id");
			
			if(this.checked){
				
				selectedSet.add(
					String(id)
				);
				
			}else{
				
				selectedSet.delete(
					String(id)
				);
			}
		}
	);
	table.on("draw", function(){
		refreshIndExpenseChart();
	});
}

/* ===================== UPLOAD ===================== */

document.getElementById(
	"uploadForm"
).onsubmit = async (e) => {
	
	e.preventDefault();
	
	const btn =
	e.target.querySelector("button");
	
	btn.disabled = true;
	
	btn.innerText = "Uploading...";
	
	try{
		
		const res = await fetch(
			"/upload",
			{
				method: "POST",
				body: new FormData(e.target)
			}
		);
		
		const data = await res.json();
		
		if(data.error){
			
			alert(data.error);
			
			return;
		}
		
		allRecords =
		data.records || [];
		
		matchedRecords =
		data.matched || [];
		
		renderSummary(
			data.summary || {}
		);
		
		initTable(allRecords);
		
		renderMatched(matchedRecords);
		
		refreshPie();
		
		refreshBarChart();
		
		refreshIndExpenseChart();
		
	} finally {
		
		btn.disabled = false;
		
		btn.innerText = "Upload File";
	}
};

/* ===================== MATCHED ===================== */

function renderMatched(data){
	
	const tbody =
	document.querySelector(
		"#matchedTable tbody"
	);
	
	tbody.innerHTML = "";
	
	data.forEach(r => {
		
		tbody.innerHTML += `
		<tr>
		
		<td>${r.date || "-"}</td>
		
		<td>
		₹${Number(
			r.credited_amt || 0
		).toFixed(2)}
		</td>
		
		<td>
		${r.received_from || "-"}
		</td>
		
		<td>
		₹${Number(
			r.cancelled_amt || 0
		).toFixed(2)}
		</td>
		
		<td>
		${r.paid_to || "-"}
		</td>
		
		</tr>
		`;
	});
}

/* ===================== PIE CHART ===================== */

function refreshPie(){
	
	const data = allRecords;
	
	if(!data.length) return;
	
	const grouped = {};
	
	data.forEach(r => {
		
		const g =
		r.group || "Ungrouped";
		
		grouped[g] =
		(grouped[g] || 0) +
		Number(r.amt || 0);
	});
	
	if(chart) chart.destroy();
	
	chart = new Chart(
		
		document.getElementById(
			"pieChart"
		),
		
		{
			type: "doughnut",
			
			data: {
				
				labels:
				Object.keys(grouped),
					  
					  datasets: [{
						  
						  data:
						  Object.values(grouped),
					  
					  backgroundColor:
					  Object.keys(grouped)
					  .map(getColor)
					  }]
			},
			
			options: {
				
				cutout: "70%",
				
				plugins: {
					
					legend: {
						position: "bottom"
					}
				}
			}
		}
	);
}

/* ===================== TOP 10 EXPENSES ===================== */

function refreshBarChart() {
	
	const data = allRecords;
	
	if (!data.length) return;
	
	const grouped = {};
	
	data.forEach(r => {
		
		const g = r.group || "Ungrouped";
		
		// 👇 same toggle behavior as Chart2
		if (hiddenGroups.has(g)) return;
		
		grouped[g] = (grouped[g] || 0) + Number(r.amt || 0);
	});
	
	const sorted = Object.entries(grouped)
	.sort((a, b) => b[1] - a[1])
	.slice(0, 10);
	
	barLabels = sorted.map(x => x[0]);
	const values = sorted.map(x => x[1]);
	
	if (barChart) barChart.destroy();
	
	barChart = new Chart(document.getElementById("barChart"), {
		type: "bar",
		
		data: {
			labels: barLabels,
			datasets: [{
				label: "₹ Top Expenses",
				data: values,
				backgroundColor: barLabels.map(getColor),
						 borderRadius: 10,
						 borderSkipped: false
			}]
		},
		
		options: {
			responsive: true,
			maintainAspectRatio: false,
			
			// ✅ CLICK BEHAVIOR (same as Chart2)
			onClick: (e, elements) => {
				
				if (!elements.length) return;
				
				const index = elements[0].index;
				const clickedGroup = barLabels[index];
				
				if (hiddenGroups.has(clickedGroup)) {
					hiddenGroups.delete(clickedGroup);
				} else {
					hiddenGroups.add(clickedGroup);
				}
				
				refreshBarChart();
			},
			
			plugins: {
				legend: {
					display: false
				},
				
				tooltip: {
					callbacks: {
						label: ctx => `₹${ctx.raw.toFixed(2)}`
					}
				}
			},
			
			scales: {
				x: {
					grid: { display: false },
					ticks: {
						maxRotation: 45,
						minRotation: 25
					}
				},
				
				y: {
					beginAtZero: true,
					grid: {
						color: "rgba(0,0,0,0.06)"
					},
					ticks: {
						callback: value => `₹${value}`
					}
				}
			}
		}
	});
}

function getActiveTableData(){
	if(table){
		return table.rows({ search: "applied" }).data().toArray();
	}
	return allRecords;
}
/* ===================== TOP 10 Individual Exp ===================== */

function refreshIndExpenseChart(){
	
	const data = getActiveTableData();
	
	if(!data.length) return;
	
	/* individual transactions */
	
	const sorted = [...data]
	
	.sort((a,b) =>
	Number(b.amt || 0) -
	Number(a.amt || 0)
	)
	
	.slice(0, 10);
	
	const labels = sorted.map(r => {
		
		const merchant =
		r.paid_to || "Unknown";
		
		const date =
		r.date || "";
		
		return `${merchant} (${date})`;
	});
	
	const values = sorted.map(r =>
	Number(r.amt || 0)
	);
	
	if(IntExpenseChart){
		IntExpenseChart.destroy();
	}
	
	IntExpenseChart = new Chart(
		
		document.getElementById(
			"IntExpenseChart"
		),
		
		{
			type: "bar",
			
			data: {
				
				labels,
				
				datasets: [{
					
					label:
					"₹ Top Individual Expenses",
					
					data: values,
					
					backgroundColor:
					labels.map((_, i) =>
					palette[i % palette.length]
					),
					
					borderRadius: 10,
					
					borderSkipped: false
				}]
			},
			
			options: {
				
				responsive: true,
				
				maintainAspectRatio: false,
				
				plugins: {
					
					legend: {
						display: false
					},
					
					tooltip: {
						
						callbacks: {
							
							label: ctx =>
							`₹${ctx.raw.toFixed(2)}`
						}
					}
				},
				
				scales: {
					
					x: {
						
						grid: {
							display: false
						},
						
						ticks: {
							maxRotation: 45,
							minRotation: 25
						}
					},
					
					y: {
						
						beginAtZero: true,
						
						grid: {
							color:
							"rgba(0,0,0,0.06)"
						},
						
						ticks: {
							
							callback: value =>
							`₹${value}`
						}
					}
				}
			}
		}
	);
}

/* ===================== SAVE GROUP ===================== */

async function saveGroup(){
	
	const group =
	document.getElementById("groupName").value.trim();
	
	if(!group){
		alert("Enter group name");
		return;
	}
	
	const mode =
	document.getElementById("groupMode").value;
	
	const selected =
	allRecords.filter(
		r => selectedSet.has(String(r.id))
	);
	
	if(!selected.length){
		alert("Select transactions");
		return;
	}
	
	// choose grouping field based on dropdown
	const entities = [
		...new Set(
			selected.map(r => {
				
				if(mode === "notes"){
					return (r.notes || "").toLowerCase().trim();
				}
				
				// default paid_to
				return (r.paid_to || "").toLowerCase().trim();
			})
		)
	];
	
	const res = await fetch("/save_group", {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify({
			group,
			mode,          // 👈 IMPORTANT ADDITION
			entities
		})
	});
	
	const data = await res.json();
	
	if(data.success){
		
		alert("Group saved!");
		
		selected.forEach(r => {
			r.group = group;
		});
		
		selectedSet.clear();
		
		initTable(allRecords);
		refreshPie();
		refreshBarChart();
		refreshIndExpenseChart();
	}
}
