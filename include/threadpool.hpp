#ifndef RBTHREADPOOL_H
#define RBTHREADPOOL_H

#include <thread>
#include <queue>
#include <functional>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <cassert>

/* Robert Capps 03-14-2019
   implemented with a lot of guidance from:
   https://stackoverflow.com/a/51400041 */

class ThreadPool
{
private:
  std::queue<std::function<void()>> m_func_q;
  std::mutex m_lock;
  std::condition_variable m_dcond;
  std::atomic<bool> m_accept_func;
  
public:
  ThreadPool();
  ~ThreadPool();
  void push(std::function<void()> func);
  void done();
  void loop_func();
};

ThreadPool::ThreadPool() : m_func_q(), m_lock(), m_dcond(), m_accept_func(true)
{
}

ThreadPool::~ThreadPool()
{
}

void ThreadPool::push(std::function<void()> func)
{
  std::unique_lock<std::mutex> lock(m_lock);
  m_func_q.push(func);
  lock.unlock();
  m_dcond.notify_one();
}

void ThreadPool::done()
{
  std::unique_lock<std::mutex> lock(m_lock);
  m_accept_func = false;
  lock.unlock();
  m_dcond.notify_all();
}

void ThreadPool::loop_func()
{
  std::function<void()> func;
  while(true)
    {
      {
	std::unique_lock<std::mutex> lock(m_lock);
	m_dcond.wait(lock, [this]() { return !m_func_q.empty() || !m_accept_func; });
	if (!m_accept_func && m_func_q.empty())
	  {
	    // end thread loop, lock is released immediately
	    return;
	  }
	func = m_func_q.front();
	m_func_q.pop(); // release the lock
      }
      func();
    }
}

#endif
