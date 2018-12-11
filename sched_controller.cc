/* Aus argos-research/genode-AdmCtrl/src/sched_controller*/

/*
 * \brief  sched_controller
 * \author Paul Nieleck
 * \date   2016/09/09
 *
 */

/* for testing in get_utilization   */
#include <random>
#include <timer_session/connection.h>
#include <string>
/* ******************************** */

#include <forward_list>
#include <unordered_map>
#include <base/printf.h>

/* for optimize function */
#include <util/xml_node.h>
#include <util/xml_generator.h>
#include <typeinfo>
/* ******************************** */

#include "sched_controller/sched_controller.h"
#include "sched_controller/task_allocator.h"
#include "sched_controller/monitor.h"
#include "mon_manager/mon_manager.h"
#include "timer_session/connection.h"

#include <cstring>

namespace Sched_controller {

	/**
	 * Initialize the run queues that are used.
	 *
	 * \param rq_size: size of the run queues,
	 *        determines how many task can be
	 *        held in the queue at once.
	 *
	 * \return 0 if finished
	 */
	int Sched_controller::_init_rqs(int rq_size)
	{

		_rqs = new Rq_buffer<Rq_task::Rq_task>[_num_cores];

		for (int i = 0; i < _num_cores; i++) {
			//_rqs[i].init_w_shared_ds(rq_size);
		}
		Genode::printf("New Rq_buffer created. Starting address is: %p.\n", _rqs);

		return 0;

	}

	/**
	 * Enqueue a new Task in the buffer
	 *
	 * \param core: which core/run queue the
	 *        task should be added to
	 * \param task: the task that should be added
	 *
	 * \return  0 if successful
	 *         <0 in any other case
	 */
	int Sched_controller::enq(int core, Rq_task::Rq_task task)
	{
		PINF("Task with name %s, is now enqueued to run queue %d", task.name, core);

		if (core < _num_cores)
		{
			task_map.insert({task.name, task});
			if(task.task_class == Rq_task::Task_class::hi)
			{
				//Execute sufficient schedulability test
				if (!fp_alg.fp_sufficient_test(&task, &_rqs[core]))
				{
					//If sufficient test fails --> execute RTA (exact test)
					if (!fp_alg.RTA(&task, &_rqs[core]))
					{
						return -1;
					}
				}
				PWRN("Sched_controller (enq): Task %s was rta analyzed", task.name);
			}
			else if (task.task_class == Rq_task::Task_class::lo)
			{
				// do task optimization for lo tasks
				_optimizer->add_task((unsigned int) core, task);
			}
			else
			{
				PWRN("Sched_controller (enq): The task_class of task %s is neither hi nor lo. It is: %d", task.name, task.task_class);
			}
			int success = _rqs[core].enq(task);

			return success;
		}
		else
		{
			PWRN("Sched_controller (enq): At task %s, the core (%d) is larger or equal than the number of cores (%d)", task.name, core, _num_cores);
		}

		return -1;
	}

	/**
	 * Dequeue a task from a given run queue
	 *
	 * \param core: specify the run queue from which
	 *        the element should be dequeued
	 * \param **task_ptr: pointer that will be set
	 *        to the location where the task is stored
	 */
	int Sched_controller::deq(int core, Rq_task::Rq_task **task_ptr)
	{

		if (core < _num_cores) {
			int success = _rqs[core].deq(task_ptr);
			PINF("Removed task from core %d, pointer is %p", core, *task_ptr);
			return success;
		}

		return -1;
	}

	void Sched_controller::init_ds(int num_rqs, int num_cores)
	{
		int ds_size = num_cores*(4 * sizeof(int)) + (num_rqs * sizeof(Rq_task::Rq_task));
		_rqs = new Rq_buffer<Rq_task::Rq_task>[num_cores];
		for (int i = 0; i < num_cores; i++) {
			sync_ds_cap_vector.emplace_back(Genode::env()->ram_session()->alloc(ds_size));
			_rqs[i].init_w_shared_ds(sync_ds_cap_vector.back());
		}
	}

	void Sched_controller::set_sync_ds(Genode::Dataspace_capability ds_cap)
	{
		PDBG("Got ds cap\n");
		_num_cores=1;
		sync_ds_cap=ds_cap;
		_rqs = new Rq_buffer<Rq_task::Rq_task>[_num_cores];
		for (int i = 0; i < _num_cores; i++) {
			//_rqs[i].init_w_shared_ds(sync_ds_cap);
		}

		Genode::printf("New Rq_buffer created. Starting address is: %p.\n", _rqs);
	}

	int Sched_controller::are_you_ready()
	{
		the_cycle();
		return 0;
	}

	/**
	 * Get and set the number of available physically
	 * available CPU cores of the system.
	 * This function will not change the number of
	 * _pcore objects.
	 *
	 * \return success status
	 */
	int Sched_controller::_set_num_pcores()
	{
		_num_pcores = _mon_manager.get_num_cores();
		_num_cores=_num_pcores;
		PDBG("Num cores=%d\n", _num_cores);
		return 0;
	}

	/**
	 * Initialize the pcores, i.e. create new
	 * instances of the pcore class
	 *
	 * \return success status
	 */
	int Sched_controller::_init_pcores()
	{

		_pcore = new Pcore[_num_pcores];

		for (int i = 0; i < _num_pcores; i++) {
			_pcore[i].set_id(i);
		}

		return 0;
	}

	/**
	 * Initialize the run queues
	 *
	 * \return success status
	 */
	int Sched_controller::_init_runqueues()
	{

		/* currently this is pretty stupid and
		 * not what we actually want.
		 */

		/* For the final implementation it is actually planned
		 * to initialize the run queues dynamically, but therefore
		 * the rq_manager has to be changed accordingly. At the
		 * moment the rq_manager is configured to provide a fixed
		 * number of run queues.
		 */
		//_num_rqs = _rq_manager.get_num_rqs();
		PINF("Number of supplied run queues is: %d", _num_rqs);

		_runqueue = new Runqueue[_num_rqs];

		for (int i = 0; i < _num_pcores; i++) {
			_runqueue[i]._task_class = Rq_task::Task_class::lo;
			_runqueue[i]._task_strategy = Rq_task::Task_strategy::priority;
			_runqueue[i].rq_buffer = i;
		}

		return 0;
	}

	/**
	 * Call the Task_allocator to allocate newly arriving tasks
	 * (comming in via the respective RPC-call) to a sufficient
	 * pcore/rq_buffer.
	 *
	 * \param newly arriving task
	 */
	void Sched_controller::allocate_task(Rq_task::Rq_task task)
	{

		PINF("Start allocating Task with id %d", task.task_id);
		Task_allocator::allocate_task(this, &task);

	}

	void Sched_controller::task_to_rq(int rq, Rq_task::Rq_task *task) {
		//PINF("Number of RQs: %d", _rq_manager.get_num_rqs());
		int status = enq(rq, *task);
		//PDBG("%d", status);
		return;
	}






	/**
	*
	* Optimize edf task scheduling at overload
	*
	*/
	Sched_opt* Sched_controller::get_optimizer()
	{
		return _optimizer;
	}






	/**
	 *
	 */
	int Sched_controller::get_num_rqs()
	{
		return _num_rqs;
	}

	int Sched_controller::get_num_cores()
	{
		return _num_cores;
	}

	/**
	 * Return the run queues that support the requested task_class
	 * and task_strategy.
	 *
	 * \param
	 *
	 */
	void Sched_controller::which_runqueues(std::vector<Runqueue> *rq, Rq_task::Task_class task_class, Rq_task::Task_strategy task_strategy)
	{
		rq->reserve(_num_rqs);
		for (int i = 0; i < _num_rqs; i++) {
			if (_runqueue[i]._task_class == task_class) {
				if (_runqueue[i]._task_strategy == task_strategy) {
					rq->push_back(_runqueue[i]);
				}
			}
		}

		return;
	}

	/**
	 * Computes the utilization of the requested runqueue.
	 *
	 * \return Utilization of the runqueue. The utilization
	 *         should usually be between 0 and 1. In cases
	 *         where too many tasks are scheduled on one
	 *         core/runqueu, the utilization might also be
	 *         > 1.
	 */

	double Sched_controller::get_utilization(int core) {
		switch(core){
			case 0:	return _mon_manager.get_util(0);
			case 1: return _mon_manager.get_util(1);
			case 2: return _mon_manager.get_util(2);
			case 3: return _mon_manager.get_util(3);
			default: return -1;
		}
	}

	/**
	 * Get a list of pcores that are assigned no runqueues
	 *
	 * \return forward_list containing pointers to the pcores
	 */
	std::forward_list<Pcore*> Sched_controller::get_unused_cores()
	{

		/*
		 * TODO: Find a way to erase elements directly form pcores
		 *       instead of creating another unused_pcores list and
		 *       pushing elemnts in there.
		 */
		std::forward_list<Pcore*> pcores = Pcore::get_pcores();
		std::forward_list<Pcore*> unused_pcores;

		for (auto it = pcores.begin(); it != pcores.end(); it++) {
			/*
			 * has the pcore any runqueues associated? If it hasn't, it can not
			 * be found in the _pcore_rq_association unordered_multimap
			 */
			if (_pcore_rq_association.find(*it) == _pcore_rq_association.end()) {
				PDBG("Pcore has no RQ, it claims...");
				unused_pcores.push_front(*it);
			}
		}

		return unused_pcores;
	}

	/******************
	 ** Constructors **
	 ******************/

	Sched_controller::Sched_controller()
	{
		/* We then need to figure out how many CPU cores are available at the system */
		_set_num_pcores();

		/* And finally we will create instances of _pcore */
		_init_pcores();

		/* Now lets create the runqueues we're working with */
		_init_runqueues();

		_rqs = new Rq_buffer<Rq_task::Rq_task>[_num_cores];

		mon_ds_cap = Genode::env()->ram_session()->alloc(100*sizeof(Mon_manager::Monitoring_object));
		Mon_manager::Monitoring_object *threads = Genode::env()->rm_session()->attach(mon_ds_cap);

		rq_ds_cap = Genode::env()->ram_session()->alloc(101*sizeof(int));
		rqs=Genode::env()->rm_session()->attach(rq_ds_cap);

		sync_ds_cap = Genode::env()->ram_session()->alloc(100*sizeof(int));
		_rqs[0].init_w_shared_ds(sync_ds_cap);

		dead_ds_cap = Genode::env()->ram_session()->alloc(256*sizeof(long long unsigned));



		rqs[1]=1;
		rqs[2]=1;
		_mon_manager.update_rqs(rq_ds_cap);

		_mon_manager.update_info(mon_ds_cap);

		idlelast0=_mon_manager.get_idle_time(0);
		idlelast1=_mon_manager.get_idle_time(1);
		idlelast2=_mon_manager.get_idle_time(2);
		idlelast3=_mon_manager.get_idle_time(3);

		//_init_rqs(_num_rqs);

		/*
		 * After we know about our run queues, we will assign them to the pcores.
		 * Currently we have 4 run queues and 4 pcores. Hence we can make a fixed
		 * assignement.
		 *
		 * ATTENTION: This implementation is only for testing until run queues can
		 *            be created dynamically!
		 */
		for (int i = 0; i < _num_rqs; i++) {
			std::pair<Pcore*, Runqueue*> _pcore_rq_pair (_pcore + i, _runqueue + i);
			_pcore_rq_association.insert(_pcore_rq_pair);
			//PINF("Allocated rq_buffer %d to _pcore %d", i, i);
		}

		_optimizer = new Sched_opt(_num_cores, &_mon_manager, threads, mon_ds_cap, dead_ds_cap);

		//loop forever
		//the_cycle();
	}

	Sched_controller::~Sched_controller()
	{

	}

	int Sched_controller::update_rq_buffer(int core)
	{
		PINF("Update Rq_buffer for core %d!", core);
		_rqs[core].init_w_shared_ds(sync_ds_cap_vector.at(core));
		Mon_manager::Monitoring_object *threads = Genode::env()->rm_session()->attach(mon_ds_cap);
		rqs[1]=1;
		rqs[2]=1;
		_mon_manager.update_rqs(rq_ds_cap);
		_mon_manager.update_info(mon_ds_cap);

		std::unordered_map<std::string, Rq_task::Rq_task>::iterator it;
		for(int i=1; i<= rqs[0]; ++i){
			Rq_task::Rq_task task;
			task.task_id = rqs[2*i-1];
			task.prio = rqs[2*i];
			for(int j=0; j<100; ++j)
			{
				if(threads[j].foc_id == task.task_id)
				{
					it = task_map.find(threads[j].thread_name.string());
					if (it != task_map.end())
					{
						task.wcet = it->second.wcet;
						task.inter_arrival = it->second.inter_arrival;
						task.deadline = it->second.deadline;
						strcpy(task.name, it->second.name);
						_rqs[core].enq(task);
					}
					break;
				}
				if(threads[j].foc_id == 0 && threads[j].prio == 0)
				{
					break;
				}
			}
		}
		return 0;
	}

	void Sched_controller::the_cycle() {
		rqs[1]=1;
		rqs[2]=1;
		_mon_manager.update_rqs(rq_ds_cap);
		_rqs[0].init_w_shared_ds(sync_ds_cap);
		_rqs[1].init_w_shared_ds(sync_ds_cap);
		for(int i=1;i<=rqs[0];i++)
		{
			Rq_task::Rq_task task;
			task.task_id = rqs[2*i-1];
			task.task_class = Rq_task::Task_class::lo;
			task.task_strategy = Rq_task::Task_strategy::priority;
			task.prio = rqs[2*i];
			//PDBG("enqueue task\n");
			//allocate_task(task);
			_rqs->enq(task);
		}
		//guess number of tasks in rq smaller than 50
		Genode::Ram_dataspace_capability _ds=Genode::env()->ram_session()->alloc(100*sizeof(int));
		int *list=Genode::env()->rm_session()->attach(_ds);;
		//count number of tasks dequeued from rq buffer
		int counter=1;
		//object pointer to temporarily store dequeued task
		Rq_task::Rq_task *dequeued_task;
		while(1)
		{
			//stop dequeueing, if there are no more tasks in the buffer
			if(dequeued_task==nullptr) break;
			//Store tuples of id and prio in list for core
			list[2*counter]=(*dequeued_task).task_id;
			list[2*counter+1]=(*dequeued_task).prio;
			Genode::printf("dequeue task id:%d prio:%d\n",(*dequeued_task).task_id,(*dequeued_task).prio);
			counter++;
		}
		//store number of tuples at first position of array
		list[0]=counter-1;
		list[1]=1;
		sync.deploy(_ds, 0, 0);
		Genode::env()->ram_session()->free(_ds);
		the_cycle();
	}

}
