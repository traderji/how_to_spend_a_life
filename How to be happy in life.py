# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 13:42:06 2018

@author: yji
"""
import numpy as np
from abc import ABCMeta, abstractmethod
import matplotlib.pyplot as plt
import six

#average life expectation is 75years, and that is 75 * 365  = 27375 days
K_INIT_LIVING_DAYS = 27375

class Person(object):
    
    """ 
    object human
    """
    
    def __init__(self):
        
        #initialize life expectency, happiness index, wealth and fame
        self.living = K_INIT_LIVING_DAYS
        self.happiness = 0
        self.wealth = 0
        self.fame = 0
        self.living_day = 0
    
    def live_one_day(self, seek):
        """
        what are you seeking in your life?
        you can only seek for one thing in a given day
        :param seek:
        :return:
        """
        
        consume_living, happiness, wealth, fame = seek.do_seek_day()
        self.living -= consume_living 
        self.happiness += happiness
        self.wealth += wealth
        self.fame += fame
        self.living_day += 1
        
        
        
class BaseSeekDay(six.with_metaclass(ABCMeta, object)):
    
    def __init__(self):
         
        self.living_consume = 0
        self.happiness_base = 0
        self.wealth_base = 0
        self.fame_base = 0

        self.living_factor = [0]
        self.happiness_factor = [0]
        self.wealth_factor = [0]
        self.fame_factor = [0]
        self.do_seek_day_cnt = 0
        self._init_self()
        
    @abstractmethod
    def _init_self(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def _gen_living_days(self, *args, **kwargs):
        pass
    
    def do_seek_day(self):
        """
        defines what do you seek on everyday
        :return:
        """
        
        #consume_living
        if self.do_seek_day_cnt >= len(self.living_factor):
            consume_living = self.living_factor[-1] * self.living_consume

        else:
            consume_living = self.living_factor[self.do_seek_day_cnt] * self.living_consume


        #happiness
        if self.do_seek_day_cnt >= len(self.happiness_factor):
             
            # marginal utility of anything is decreasing to 0
            # so happiness_factor will go :n—>0. and happiness_factor[-1]=0
            
            happiness = self.happiness_factor[-1] * self.happiness_base
        else:
            # happiness_factor will be going down
            happiness = self.happiness_factor[self.do_seek_day_cnt] * self.happiness_base

        #wealth
        if self.do_seek_day_cnt >= len(self.wealth_factor):
            wealth = self.wealth_factor[-1] * self.wealth_base
        else:
            wealth = self.wealth_factor[self.do_seek_day_cnt] * self.wealth_base

        #fame
        if self.do_seek_day_cnt >= len(self.fame_factor):
            fame = self.fame_factor[-1] * self.fame_base
        else:
            fame = self.fame_factor[self.do_seek_day_cnt] * self.fame_base
        
            
        self.do_seek_day_cnt += 1
        
        
        return consume_living, happiness, wealth, fame





def regular_mm(group):
    # normalize
    return (group - group.min()) / (group.max() - group.min())

    
class HealthSeekDay(BaseSeekDay):
    """
        HealthSeekDay-- living a health and hapiness focused life
    """

    def _init_self(self):
        # consume 1 day
        self.living_consume = 1
        # happiness index = 1 
        self.happiness_base = 1
        self._gen_living_days()

    def _gen_living_days(self):

        days = np.arange(1, 12000.0)
        #Use sqrt to decrease the speed of reaction on living_factor
        living_days = np.sqrt(days)

        """
        living factor will grow from -1 to 1
        meaning it begins by adding life expectation but then move to reduce it
        afterall, no matter how much care you put on your health,
        you still need to die in the end

        """

        self.living_factor = regular_mm(living_days) * 2 - 1
        self.happiness_factor = regular_mm(days)[::-1]


# simulating lives


me = Person()

seek_health = HealthSeekDay()

#seeking health as long as living
while me.living > 0:
    me.live_one_day(seek_health)
    
print('living healthy for {} years，happiness{},wealth{},fame{}'.format
      (round(me.living_day / 365, 2), round(me.happiness, 2), me.wealth, me.fame))
      
      
      


plt.plot(seek_health.living_factor * seek_health.living_consume)
plt.plot(seek_health.happiness_factor * seek_health.happiness_base)
plt.legend(['living_factor', 'happiness_factor'], loc='best')



class StockSeekDay(BaseSeekDay):
    """
    spend the days chasing wealth -- a professional stock investor
    """

    def _init_self(self, show=False):

        self.living_consume = 2
        self.happiness_base = 0.5
        self.wealth_base = 10
        self._gen_living_days()

    def _gen_living_days(self):
        days = np.arange(1, 10000.0)
        living_days = np.sqrt(days)
        self.living_factor = regular_mm(living_days)
        
        #a faster decrease of hapiness factor
        happiness_days = np.power(days, 4)
        self.happiness_factor = regular_mm(happiness_days)[::-1]
        

        self.wealth_factor = self.living_factor


class FameSeekDay(BaseSeekDay):
  
    def _init_self(self):
        self.living_consume = 3
        self.happiness_base = 0.6
        self.fame_base = 10
        self._gen_living_days()

    def _gen_living_days(self):
        days = np.arange(1, 12000)
        living_days = np.sqrt(days)
        self.living_factor = regular_mm(living_days)

        happiness_days = np.power(days, 2)
        self.happiness_factor = regular_mm(happiness_days)[::-1]
        self.fame_factor = self.living_factor
        

        
"""
Use Monte-Carlo to decide what is the best combination of Health, Wealth and Fame
"""

def my_life(weights):

    # weights are the weights of three part of life:
    seek_health = HealthSeekDay()
    seek_stock = StockSeekDay()
    seek_fame = FameSeekDay()

    # a list to map to choice() below
    seek_list = [seek_health, seek_stock, seek_fame]


    me = Person()
    # randomly choose 80k days
    seek_choice = np.random.choice([0, 1, 2], 80000, p=weights)

    while me.living > 0:
        seek_ind = seek_choice[me.living_day]
        seek = seek_list[seek_ind]
        me.live_one_day(seek)
    return round(me.living_day / 365, 2), round(me.happiness, 2), \
        round(me.wealth, 2), round(me.fame, 2)
